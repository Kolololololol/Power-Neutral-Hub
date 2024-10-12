from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import zipfile
import rarfile
from flask_migrate import Migrate
from datetime import datetime
from models import db, Object, Photo, Result, MisclassifiedPhoto
from flask_cors import CORS
from utils import start_detect_defects
from flask import send_from_directory
import shutil
from datetime import datetime, timedelta
from const_params import RU_MODEL_CLASS_NAMES 
from flask import send_file
from converts import save_as_json, get_json_file, save_as_docx, save_as_pdf
from PIL import Image


app = Flask(__name__)

# Настройка базы данных
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost:15432/hacks"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@db:5432/hacks"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Обработчик для загрузки файлов
@app.route('/upload/', methods=['POST'])
def upload_files():
    session = db.session()
    try:
        # Получаем серийный номер
        serial_number = request.form.get('serial_number')
        if not serial_number:
            return jsonify({"error": "Серийный номер обязателен"}), 400

        # Получаем файлы
        files = request.files.getlist('files')
        if not files:
            return jsonify({"error": "Файлы обязательны"}), 400

        # Создаем объект с серийным номером
        db_object = Object(serial_number=serial_number)
        session.add(db_object)
        session.commit()
        session.refresh(db_object)

        # Создаем папки для загрузки файлов
        base_path = os.path.join(app.config['UPLOAD_FOLDER'], serial_number)
        input_path = os.path.join(base_path, "input")
        output_path = os.path.join(base_path, "output")
        os.makedirs(input_path, exist_ok=True)
        os.makedirs(output_path, exist_ok=True)

        # Обработка загруженных файлов
        for file in files:
            filename = secure_filename(file.filename)
            file_location = os.path.join(input_path, filename)
            file.save(file_location)

            # Распаковка архивов, если файл является zip или rar
            if filename.endswith(".zip"):
                with zipfile.ZipFile(file_location, 'r') as zip_ref:
                    zip_ref.extractall(input_path)
                os.remove(file_location)
            elif filename.endswith(".rar"):
                with rarfile.RarFile(file_location) as rar_ref:
                    rar_ref.extractall(input_path)
                os.remove(file_location)

        # Добавляем все файлы из input_path в БД
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                db_photo = Photo(object_id=db_object.id, file_path_input=file_path)
                session.add(db_photo)

        session.commit()

        # Запуск обработки фотографий через нейронную сеть
        detect_results = start_detect_defects(serial_number)

        # Обновление данных в БД после обработки фотографий
        for img_path, result_info in detect_results['imgs_info'].items():
            photo = session.query(Photo).filter(Photo.file_path_input == os.path.join(input_path, img_path)).first()
            if photo:
                output_file_path = os.path.join(output_path, os.path.basename(img_path))
                photo.file_path_output = output_file_path
                photo.recognition_date = datetime.utcnow()
                photo.recognized = True
                session.add(photo)

                # Сохранение результата для каждого класса дефекта
                for defect_class, count in result_info.items():
                    for _ in range(count):
                        db_result = Result(photo_id=photo.id, recognized_class=defect_class)
                        session.add(db_result)

        session.commit()

        return jsonify({"message": "Файлы успешно загружены и обработаны"})

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

# Обработчик для получения статистики
@app.route('/statistics/', methods=['GET'])
def get_statistics():
    session = db.session()
    try:
        # Основная статистика
        recognized_objects = session.query(Object).count()
        detected_defects = session.query(MisclassifiedPhoto).count()
        photos_uploaded = session.query(Photo).count()
        defect_photos = session.query(Photo).filter(Photo.recognized == False).count()

        # Подсчет дефектов по классам на основе RU_MODEL_CLASS_NAMES
        class_stats = {}
        for class_id, class_name in RU_MODEL_CLASS_NAMES.items():
            count = session.query(Result).filter(Result.recognized_class == class_name).count()
            class_stats[class_name] = count

        # Временные рамки для анализа изменений
        today = datetime.utcnow().date()
        one_day_ago = today - timedelta(days=1)
        one_week_ago = today - timedelta(weeks=1)
        one_month_ago = today - timedelta(days=30)

        # Фильтры для изменений за день, неделю и месяц
        recognized_objects_day = session.query(Object).filter(Object.photos.any(Photo.upload_date >= one_day_ago)).count()
        recognized_objects_week = session.query(Object).filter(Object.photos.any(Photo.upload_date >= one_week_ago)).count()
        recognized_objects_month = session.query(Object).filter(Object.photos.any(Photo.upload_date >= one_month_ago)).count()

        photos_uploaded_day = session.query(Photo).filter(Photo.upload_date >= one_day_ago).count()
        photos_uploaded_week = session.query(Photo).filter(Photo.upload_date >= one_week_ago).count()
        photos_uploaded_month = session.query(Photo).filter(Photo.upload_date >= one_month_ago).count()

        detected_defects_day = session.query(MisclassifiedPhoto).filter(MisclassifiedPhoto.created_at >= one_day_ago).count()
        detected_defects_week = session.query(MisclassifiedPhoto).filter(MisclassifiedPhoto.created_at >= one_week_ago).count()
        detected_defects_month = session.query(MisclassifiedPhoto).filter(MisclassifiedPhoto.created_at >= one_month_ago).count()

        # Формирование ответа
        response_data = {
            "recognized_objects": recognized_objects,
            "detected_defects": detected_defects,
            "photos_uploaded": photos_uploaded,
            "defect_photos": defect_photos,
            "class_stats": class_stats,
            "changes": {
                "day": {
                    "recognized_objects": recognized_objects_day,
                    "photos_uploaded": photos_uploaded_day,
                    "detected_defects": detected_defects_day
                },
                "week": {
                    "recognized_objects": recognized_objects_week,
                    "photos_uploaded": photos_uploaded_week,
                    "detected_defects": detected_defects_week
                },
                "month": {
                    "recognized_objects": recognized_objects_month,
                    "photos_uploaded": photos_uploaded_month,
                    "detected_defects": detected_defects_month
                }
            }
        }

        return jsonify(response_data)
    finally:
        session.close()


# Обработчик для получения истории
@app.route('/history/', methods=['GET'])
def get_history():
    session = db.session()
    try:
        history = session.query(Object).all()
        result = [
            {
                "serial_number": obj.serial_number,
                "date": obj.photos[0].upload_date if obj.photos else None,
                "photo": obj.photos[0].file_path_output if obj.photos else None,
            }
            for obj in history
        ]
        return jsonify(result)
    finally:
        session.close()

@app.route('/history/<string:serial_number>/', methods=['GET'])
def get_full_history(serial_number):
    session = db.session()
    try:
        db_object = session.query(Object).filter(Object.serial_number == serial_number).first()
        if not db_object:
            return jsonify({"error": "Объект не найден"}), 404

        result = {
            "serial_number": db_object.serial_number,
            "photos": [
                {
                    "id": photo.id,
                    "file_path_input": photo.file_path_input,
                    "file_path_output": photo.file_path_output,
                    "recognized": photo.recognized,
                    "results": [
                        {
                            "recognized_class": result.recognized_class
                        }
                        for result in session.query(Result).filter(Result.photo_id == photo.id).all()
                    ]
                }
                for photo in db_object.photos
            ]
        }
        return jsonify(result)
    finally:
        session.close()

@app.route('/static/<path:filename>', methods=['GET'])
def get_photo(filename):
    return send_from_directory('static', filename)

@app.route('/save_misclassified/', methods=['POST'])
def save_misclassified():
    data = request.get_json()
    
    # Извлечение данных из запроса
    photo_id = data.get("photo_id")
    correct_class = data.get("correct_class")
    x_coord = data.get("x_coord")
    y_coord = data.get("y_coord")
    width = data.get("width")
    height = data.get("height")

    # Получение информации о фотографии
    session = db.session()
    photo = session.query(Photo).filter(Photo.id == photo_id).first()

    if not photo:
        return jsonify({"error": "Фото не найдено"}), 404

    try:
        # Получение размера изображения
        original_photo_path = photo.file_path_input
        with Image.open(original_photo_path) as img:
            img_width, img_height = img.size

        # Сохранение информации о неверно классифицированном фото в базу данных
        misclassified = MisclassifiedPhoto(
            photo_id=photo_id,
            correct_class=correct_class,
            x_coord=x_coord,
            y_coord=y_coord,
            width=width,
            height=height
        )
        session.add(misclassified)
        session.commit()

        # Создание директории для сохранения исправленных фотографий и текстовых файлов
        misclassified_dir = os.path.join('static', 'misclassified')
        if not os.path.exists(misclassified_dir):
            os.makedirs(misclassified_dir)

        # Копирование файла фотографии в папку "misclassified"
        new_photo_path = os.path.join(misclassified_dir, os.path.basename(original_photo_path))
        shutil.copyfile(original_photo_path, new_photo_path)

        # Создание .txt файла с информацией о выделенных областях
        txt_file_path = os.path.splitext(new_photo_path)[0] + '.txt'
        with open(txt_file_path, 'w') as f:
            # Записываем координаты и класс в YOLO-формате (нормализованные значения)
            x_center = (x_coord + width / 2) / img_width
            y_center = (y_coord + height / 2) / img_height
            norm_width = width / img_width
            norm_height = height / img_height

            # Определение индекса класса из RU_MODEL_CLASS_NAMES
            class_mapping = {v: k for k, v in RU_MODEL_CLASS_NAMES.items()}
            class_index = class_mapping.get(correct_class, -1)

            if class_index != -1:
                f.write(f"{class_index} {x_center} {y_center} {norm_width} {norm_height}\n")

        return jsonify({"message": "Данные успешно сохранены и файл создан"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

# Путь до результатов диагностики
PATH_TO_DETECT_RESULTS = './static'

# Получение JSON-файла
@app.route('/report/<string:serial_number>/json', methods=['GET'])
def get_json_report(serial_number):
    try:
        json_file_path = get_json_file(serial_number)
        if not os.path.exists(json_file_path):
            return jsonify({"error": "JSON отчет не найден"}), 404
        return send_file(json_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Получение DOCX-файла
@app.route('/report/<string:serial_number>/docx', methods=['GET'])
def get_docx_report(serial_number):
    try:
        # Генерация DOCX, если его еще нет
        save_as_docx(serial_number)
        docx_file_path = os.path.join(PATH_TO_DETECT_RESULTS, serial_number, f"{serial_number}.docx")
        if not os.path.exists(docx_file_path):
            return jsonify({"error": "DOCX отчет не найден"}), 404
        return send_file(docx_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Получение PDF-файла
@app.route('/report/<string:serial_number>/pdf', methods=['GET'])
def get_pdf_report(serial_number):
    try:
        # Генерация PDF, если его еще нет
        save_as_pdf(serial_number)
        pdf_file_path = os.path.join(PATH_TO_DETECT_RESULTS, serial_number, f"{serial_number}.pdf")
        if not os.path.exists(pdf_file_path):
            return jsonify({"error": "PDF отчет не найден"}), 404
        return send_file(pdf_file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
