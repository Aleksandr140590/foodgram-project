# Проект "Продуктовый помощник"


## Описание проекта:

Приложение «Продуктовый помощник» - это сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 


## Размещение на виртуальном сервере:

1. Для установки docker & docker-compose-plugin  на серевре пожалуйста воспользуйтесь официальной документацией
```
https://docs.docker.com
```
2. Предварительные настройки
2.1. Склонируйте проект к себе на компьютер для возможности редактирования
2.2. Установите виртуальное окружение и установите зависимости из файла requirements.txt
2.3. Для размещения на сервере необходимо в настройках 
```
backend/foodgram/foodgram/settings.py
```
указать адрес хоста
2.4. Произвести сборки контейнеров фронта и бэка
2.5. В файле docker-compose.yml заменить имена образов бэка и фронта
2.6. В файле nginx.conf заменить server_name на адрес хоста

3. Скопируте на сервер файлы docker-compose.yml и nginx.conf
4. Создайте на серевере в папке где находятся файлы docker-compose.yml и nginx.conf файл .env и внесите туда следующие данные
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=//Ваши данные//
POSTGRES_USER=//Ваши данные//
POSTGRES_PASSWORD=//Ваши данные//
DB_HOST=db
DB_PORT=5433
```

5. Запустите файл docker-compose.yml ищ терминала сервера командой:
```
docker compose up -d 
```
!!! Необходимо запускать файл docker-compose из директории где он находится

6. Выполните миграции командой
```
docker compose exec backend python manage.py migrate
```

7. Создайте суперюзера
```
docker compose exec backend python manage.py createsuperuser
```
8. Необходимо собрать файлы статики
```
docker compose exec backend python manage.py collectstatic --no-input
```
9. Есть возможность внести предустановленные ингредиенты в БД
```
docker compose exec backend python manage.py load_data
```

## Техническая информация
Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

Веб-сервер: nginx (контейнер nginx)
Frontend фреймворк: React (контейнер frontend)
Backend фреймворк: Django (контейнер backend)
API фреймворк: Django REST (контейнер backend)
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.
Контейнер nginx взаимодействует с контейнером backend через gunicorn.
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

## Об авторе
Федорович Алекстандр Владимирович
Python-разработчик (Backend)
Казахстан, г. Караганда
E-mail: fedorovichalexandr@gmail.com
Telegram: https://t.me/AVFedorovich
