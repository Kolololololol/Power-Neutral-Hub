
<p align="center">
     <H2 align="center">Команда Neutral Hub</H2> 
    <H2 align="center">Определение дефектов на ноутбуках</H2> 
</p>

## Описание решения
Команда Neutral Hub представляет программный модуль определения дефектных ноутбуков по фотографиям на основе сервисной информации. Решение позволяет:
- автоматически находить и классифицировать дефекты на оборудовании по изображениям;
- формировать отчёт о наличии дефектов продукции с указанием его серийного номера, выводить его в Web-интерфейс и сохранять в удобный формат;
- снизить нагрузку на специалиста по контролю, исключив случаи невнимательности или неопытности, позволяя переключиться на выполнение других задач;
- облегчить задачу осмотра устройств в удалённых локациях и производить его в кратчайшие сроки.

Программный модуль в автоматическом формате находит и классифицирует дефекты на оборудовании по изображениям. Web-интерфейс позволяет удобно производить контроль распознавания и визуализирует отчёт. Модуль машинного распознавания обладает широким набором видов дефектов и постоянно обучается, получая новые данные.

## Особенности
- Эргономика и автономность. Постоянное самообучение и автономная адаптация нейронной сети под новые виды дефектов с повышением качества классификации. Модульная архитектура проекта позволяет гибко настраивать требуемые инструменты, а применение Docker создаёт гармоничное сочетание удобства развёртывания при высокой производительности и надёжности
-  Наглядность и функциональность. Интуитивный Web-интерфейс предоставляет возможность удобного ручного контроля операций распознавания с аннотациями на изображениях, добавлять пользовательские классы дефектов и формировать отчёт по результатам детекции в удобный формат. Система также предоставляет аналитический дашборд для специалистов, отслеживающий статистику по частоте дефектов
- Интеграция с ERP. Система имеет возможность интеграции с системами учета для автоматического сохранения результатов проверки и создания статистических отчетов на базе всех обработанных устройств


## Используемые технологии

Интерфейс: React, Material UI

Серверная часть: Flask

База данных: PostgreSQL

Контейнеризация: Docker, Docker Compose

## Запуск проекта

Для запуска проекта требуется требуется:

*1. Установить Docker Desktop с оффициального сайта.*

*2. Для запуска всего приложения в папке `/ProcurementMaterialAPI` требуется выполнить следующую команду:*

```cmd
docker-compose up --build
```

После установки всех библиотек и зависимостей будет созданно 3 docker контейнера:
- _frontend_ - с frontend частью проекта на порту 3000
- _api_ - с API на порту 8080
- _mssql_ - база данных MsSQL на порту 1433

*3. После требуется выполнить миграцию базы данных следующей командой:*

```cmd
dotnet ef database update --connection "Server=localhost,1433;Database=Materials;User=sa;Password=Passw0rd;TrustServerCertificate=True;"
```

## Руководство по фотографированию ноутбуков для более эффективного обнаружения дефектов

Для повышения эффективности обнаружения дефектов на ноутбуках рекомендуется следовать ряду правил при создании фотографий. Качественные изображения помогут значительно улучшить точность распознавания и классификации дефектов. Примеры оптимальных ракурсов:

<div style="display: flex; flex-wrap: wrap; gap: 10px;">
    <img src="1.jpg" alt="Изображение 1" width="390" style="flex: 1 1 calc(33% - 10px);"/>
    <img src="2.jpg" alt="Изображение 2" width="390" style="flex: 1 1 calc(33% - 10px);"/>
    <img src="5.jpg" alt="Изображение 3" width="390" style="flex: 1 1 calc(33% - 10px);"/>
    <img src="6.jpg" alt="Изображение 4" width="390" style="flex: 1 1 calc(33% - 10px);"/>
    <div>
     <img src="3.jpg" alt="Изображение 5" width="390" style="flex: 1 1 calc(33% - 10px);"/>
    <img src="4.jpg" alt="Изображение 6" width="390" style="flex: 1 1 calc(33% - 10px);"/>
    </div>
</div>

Следование этим рекомендациям обеспечит более эффектичвное распознавание дефектов на ноутбуке системой анализа.

## Пример отчета в виде PDF

[example.pdf](https://github.com/user-attachments/files/17351323/example.pdf)


### Пример работы нашего приложения вы можете увидеть на данном видео.

https://github.com/Fresh-vano/ProcurementMaterial/assets/74467916/9369635e-aad1-4a9d-8795-1c26e6a5a35c
