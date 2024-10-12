import os
import numpy as np
import pandas as pd
import datetime
import cv2
import tqdm
import time
import math
import json

from PIL import Image, ImageDraw, ImageFont

from collections import defaultdict
from ultralytics import YOLO

from const_params import *
from converts import save_as_json, save_as_docx, save_as_pdf

MODEL = YOLO(PATH_TO_NEURAL_MODEL)
MODEL_CLASSES = RU_MODEL_CLASS_NAMES


def predict_one_img(img):
    """ Получение предикта по обработке изображения """
    global MODEL

    try:
        return MODEL.predict(img, conf=0.5)[0]
    except:
        print("[ERROR]")
        return None


def draw_predicted_box(img, results):
    global MODEL, MODEL_CLASSES

    image_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # Использовать шрифт, поддерживающий кириллицу (укажите путь к .ttf файлу шрифта)
    # Задаем размер шрифта пропорционально высоте изображения
    font_size = int(img.shape[1] / 40)
    if font_size < 20:
        font_size = 20

    font_path = FONT_PATH  # Путь к файлу шрифта с кириллицей
    font = ImageFont.truetype(font_path, font_size)  # Размер шрифта

    rectange_width = int(img.shape[1] / 300)
    if not rectange_width:
        rectange_width = 2

    # Перебрать все предсказания
    for result in results.boxes:
        # Получить координаты рамки
        box = result.xyxy[0]  # [x_min, y_min, x_max, y_max]
        x1, y1, x2, y2 = map(int, box)

        # Получить идентификатор класса и уверенность
        class_id = int(result.cls[0])
        confidence = result.conf[0]
        class_name = MODEL_CLASSES[class_id]  # Имя класса

        # Нарисовать рамку на изображении
        draw.rectangle([x1, y1, x2, y2], outline=(
            0, 255, 0), width=rectange_width)

        # Подготовить текст с именем класса и уверенностью (поддерживается кириллица)
        label = f"{class_name} ({confidence:.2f})"

        # Найти границы текста для корректного отображения
        text_bbox = draw.textbbox((x1, y1), label, font=font, font_size=40)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        # Нарисовать фон для текста (чёрный)
        draw.rectangle([x1, y1 - text_h, x1 + text_w, y1], fill=(0, 0, 0))

        # Нарисовать текст (белый)
        draw.text((x1, y1 - text_h), label, font=font, fill=(255, 255, 255))

    # Конвертировать изображение обратно в формат OpenCV
    img = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return img


def make_detect_defect_result_info(results: list, img_path_list: list[str]) -> dict:
    """ Формирование общей структуры отчета о поиске дефектов """

    global MODEL_CLASSES

    result_info = {}

    for idx, res in enumerate(results):
        if res is None:
            # FIXME: че делать
            continue

        sub_res_info = {}

        for cls in res.boxes.cls:
            cls_name = MODEL_CLASSES[int(cls)]
            if sub_res_info.get(cls_name, -1) < 0:
                sub_res_info[cls_name] = 1
            else:
                sub_res_info[cls_name] += 1

        result_info[img_path_list[idx]] = sub_res_info

    return result_info


def detect_defects_from_img_folder(serial_number: str):
    """ Обработка загруженных фотографий на поиск дефектов """

    # получаем путь до папки с загруженными изображениями
    input_path = os.path.join(PATH_TO_DETECT_RESULTS,
                              serial_number, INPUT_FOLDER_NAME)
    # а также путь до папки с обработанными изображениями
    output_path = os.path.join(PATH_TO_DETECT_RESULTS,
                               serial_number, OUTPUT_FOLDER_NAME)

    # формируем лист наименований всех загруженных изображений
    img_path_list = os.listdir(input_path)

    # лист с cv2.Mat представлениями изображений
    img_mat_list = []
    # лист наименований успешно прочитанных изображений
    success_read_img_pathes = []

    for img_path in img_path_list:
        try:
            img = cv2.imread(os.path.join(input_path, img_path))
        except:
            print(f"[ERROR READ] {os.path.join(input_path, img_path)}")
            continue

        if img is None:
            continue

        success_read_img_pathes.append(img_path)
        img_mat_list.append(img)

    # лист с результатами распознавания
    results_list = [predict_one_img(img) for img in tqdm.tqdm(img_mat_list)]

    # наложение рамок и наименований классов на изображения
    for (idx, img) in tqdm.tqdm(enumerate(img_mat_list)):

        if len(results_list[idx].boxes):
            img = draw_predicted_box(img, results_list[idx])

        cv2.imwrite(os.path.join(
            output_path, success_read_img_pathes[idx]), img)

    # формируем стуктуру отчета
    return make_detect_defect_result_info(
        results_list, success_read_img_pathes)


def get_all_defect_info(result_info: dict) -> dict:
    """ составляем массив по всем ошибкам """
    defects_count = defaultdict(int)

    for sub_dict in result_info.values():
        for key in sub_dict:
            defects_count[key] += sub_dict[key]

    return defects_count


def start_detect_defects(serial_number: str):
    """ запуск процесса детекции дефектов, сохранение ряда параметров для отчета """

    # время в формате ISO8601 запуска распознавания дефектов
    start_detect_defect_date = datetime.datetime.now().isoformat()
    start_time = time.time()

    # проверить - есть ли docx и pdf файлы (если вдруг скинули с таким же серийным номером)
    docx_file_path = os.path.join(
        PATH_TO_DETECT_RESULTS, serial_number, f"{serial_number}.docx")
    pdf_file_path = os.path.join(
        PATH_TO_DETECT_RESULTS, serial_number, f"{serial_number}.pdf")

    if (os.path.exists(docx_file_path)):
        os.remove(docx_file_path)

    if (os.path.exists(pdf_file_path)):
        os.remove(pdf_file_path)

    # результат распознавания
    result_info = detect_defects_from_img_folder(serial_number)

    # общее время работы программы
    detect_defect_time_working = round(time.time() - start_time, 2)

    # подсчитываем общее количество ошибок
    all_defect_count = get_all_defect_info(result_info)

    # если есть хотя бы один дефект - проверка провалена
    detect_final_result = "обнаружены дефекты - устройство не прошло проверку качества." if len(
        all_defect_count) else "дефекты не обнаружены - проверка качества пройдена."

    result_dict_info = {
        # серийный номер
        "serial_number": serial_number,
        # дата в формате ISO8601 запуска детекции
        "detect_defect_date": start_detect_defect_date,
        # сколько длилось распознавание (в секундах)
        "detect_defect_working_time": detect_defect_time_working,
        # словарь вида "img_name" : {defects}
        "imgs_info": result_info,
        # словарь всех дефектов
        "all_defects": all_defect_count,
        # финальная оценка проверки (успех/провал)
        "detect_final_result": detect_final_result
    }

    # сохраняем в json
    save_as_json(result_dict_info)

    return result_dict_info


if __name__ == "__main__":
    # res = start_detect_defects("547285728945374832748902374832")
    res = start_detect_defects("example1")
    save_as_docx(res['serial_number'])
    save_as_pdf(res['serial_number'])
