# Проект «Продуктовый помощник» - Foodgram
Foodgram - Продуктовый помощник. Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в избранное, а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологический стек
![Django-app workflow](https://github.com/needred/foodgram-project-react/actions/workflows/backend.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat&color=008080)](https://jwt.io/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/)

## Как развернуть проект на сервере:
Установите соединение с сервером:
```
ssh username@server_address
```
Обновите индекс пакетов APT:
```
sudo apt update
```
и обновите установленные в системе пакеты и установите обновления безопасности:
```
sudo apt upgrade -y
```
Скопируйте подготовленный файл `docker-compose.production.yml` из вашего проекта на сервер.

Установите Docker и Docker-compose:
```
sudo apt install docker.io
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```
Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version
```
На сервере создайте файл .env 
```
sudo touch .env
```
и заполните переменные окружения.

### После успешного деплоя:
На сервере соберите docker-compose и запустите в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d
```
Соберите статические файлы (статику):
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic

sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Примените миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Создайте суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
При необходимости наполните базу тестовыми данными из backend/data/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
```

### Тестовые пользователи
Логин: ```admin``` (суперюзер)  
Email: ```admin@foodgram.ru```  
Пароль: ```1111```  

Логин: ```user1```  
Email: ```user1@foodgram.ru```  
Пароль: ```recipe_1234```  

Логин: ```user2```  
Email: ```user2@foodgram.ru```  
Пароль: ```recipe_1234```

## Пользовательские роли в проекте
1. Анонимный пользователь
2. Аутентифицированный пользователь
3. Администратор

### Анонимные пользователи могут:
1. Просматривать список рецептов;
2. Просматривать отдельные рецепты;
3. Фильтровать рецепты по тегам;
4. Создавать аккаунт.

### Аутентифицированные пользователи могут:
1. Получать данные о своей учетной записи;
2. Изменять свой пароль;
3. Просматривать, публиковать, удалять и редактировать свои рецепты;
4. Добавлять понравившиеся рецепты в избранное и удалять из избранного;
5. Добавлять рецепты в список покупок и удалять из списка;
6. Подписываться и отписываться на авторов;
7. Скачать список покупок

### Набор доступных эндпоинтов:
- ```api/docs/redoc``` - Подробная документация по работе API.
- ```api/tags/``` - Получение, списка тегов (GET).
- ```api/ingredients/``` - Получение, списка ингредиентов (GET).
- ```api/ingredients/``` - Получение ингредиента с соответствующим id (GET).
- ```api/tags/{id}``` - Получение, тега с соответствующим id (GET).
- ```api/recipes/``` - Получение списка с рецептами и публикация рецептов (GET, POST).
- ```api/recipes/{id}``` - Получение, изменение, удаление рецепта с соответствующим id (GET, PUT, PATCH, DELETE).
- ```api/recipes/{id}/shopping_cart/``` - Добавление рецепта с соответствующим id в список покупок и удаление из списка (GET, DELETE).
- ```api/recipes/download_shopping_cart/``` - Скачать файл со списком покупок TXT (в дальнейшем появиться поддержка PDF) (GET).
- ```api/recipes/{id}/favorite/``` - Добавление рецепта с соответствующим id в список избранного и его удаление (GET, DELETE).

#### Операции с пользователями:
- ```api/users/``` - получение информации о пользователе и регистрация новых пользователей. (GET, POST).
- ```api/users/{id}/``` - Получение информации о пользователе. (GET).
- ```api/users/me/``` - получение и изменение данных своей учётной записи. Доступна любым авторизованными пользователям (GET).
- ```api/users/set_password/``` - изменение собственного пароля (PATCH).
- ```api/users/{id}/subscribe/``` - Подписаться на пользователя с соответствующим id или отписаться от него. (GET, DELETE).
- ```api/users/subscribe/subscriptions/``` - Просмотр пользователей на которых подписан текущий пользователь. (GET).

#### Аутентификация и создание новых пользователей 👇:
- ```api/auth/token/login/``` - Получение токена (POST).
- ```api/auth/token/logout/``` - Удаление токена (POST).

#### Алгоритм регистрации пользователей
1. Пользователь отправляет POST-запрос для регистрации нового пользователя с параметрами
***email username first_name last_name password***
на эндпойнт ```/api/users/```
2. Пользователь отправляет POST-запрос со своими регистрационными данными ***email password*** на эндпоинт ```/api/token/login/``` , в ответе на запрос ему приходит auth-token. Примечание: При взаимодействии с фронтэндом приложения операция два происходит под капотом при переходе по эндпоинту ```/api/token/login/```.

## Ссылки
### Развёрнутый проект:
https://iultina-foodgram.sytes.net
https://iultina-foodgram.sytes.net/admin/

## Об авторе
[Iultina](https://github.com/iultina/)




[![foodgram_workflow](https://github.com/Alexey-Bormotov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/Alexey-Bormotov/foodgram-project-react/actions/workflows/foodgram_workflow.yml)
# "Продуктовый помощник" (Foodgram)

## 1. [Описание](#1)
## 2. [Установка Docker (на платформе Ubuntu)](#2)
## 3. [База данных и переменные окружения](#3)
## 4. [Команды для запуска](#4)
## 5. [Заполнение базы данных](#5)
## 6. [Техническая информация](#6)
## 7. [Об авторе](#7)

---
## 1. Описание <a id=1></a>

Проект "Продуктовый помошник" (Foodgram) предоставляет пользователям следующие возможности:
  - регистрироваться
  - создавать свои рецепты и управлять ими (корректировать\удалять)
  - просматривать рецепты других пользователей
  - добавлять рецепты других пользователей в "Избранное" и в "Корзину"
  - подписываться на других пользователей
  - скачать список ингредиентов для рецептов, добавленных в "Корзину"

---
## 2. Установка Docker (на платформе Ubuntu) <a id=2></a>

Проект поставляется в четырех контейнерах Docker (db, frontend, backend, nginx).  
Для запуска необходимо установить Docker и Docker Compose.  
Подробнее об установке на других платформах можно узнать на [официальном сайте](https://docs.docker.com/engine/install/).

Для начала необходимо скачать и выполнить официальный скрипт:
```bash
apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

При необходимости удалить старые версии Docker:
```bash
apt remove docker docker-engine docker.io containerd runc 
```

Установить пакеты для работы через протокол https:
```bash
apt update
```
```bash
apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y 
```

Добавить ключ GPG для подтверждения подлинности в процессе установки:
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

Добавить репозиторий Docker в пакеты apt и обновить индекс пакетов:
```bash
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" 
```
```bash
apt update
```

Установить Docker(CE) и Docker Compose:
```bash
apt install docker-ce docker-compose -y
```

Проверить что  Docker работает можно командой:
```bash
systemctl status docker
```

Подробнее об установке можно узнать по [ссылке](https://docs.docker.com/engine/install/ubuntu/).

---
## 3. База данных и переменные окружения <a id=3></a>

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='Здесь указать секретный ключ'
ALLOWED_HOSTS='Здесь указать имя или IP хоста' (Для локального запуска - 127.0.0.1)
```

---
## 4. Команды для запуска <a id=4></a>

Перед запуском необходимо склонировать проект:
```bash
HTTPS: git clone https://github.com/iultina/foodgram-project-react.git
SSH: git clone git@github.com:iultina/foodgram-project-react.git
```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Далее необходимо собрать образы для фронтенда и бэкенда.  
Из папки "./backend/foodgram/" выполнить команду:
```bash
docker build -t iultina/foodgram_backend .
```

Из папки "./frontend/" выполнить команду:
```bash
docker build -t iultina/foodgram_frontend .
```

Из папки "./nginx/" выполнить команду:
```bash
docker build -t iultina/foodgram_gateway .
```

После создания образов можно создавать и запускать контейнеры.  
Из папки "./infra/" выполнить команду:
```bash
docker-compose up -d
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## 5. Заполнение базы данных <a id=5></a>

С проектом поставляются данные об ингредиентах.  
Заполнить базу данных ингредиентами можно выполнив следующую команду из папки "./infra/":
```bash
docker-compose exec backend python manage.py fill_ingredients_from_csv --path data/
```

Также необходимо заполнить базу данных тегами (или другими данными).  
Для этого требуется войти в [админ-зону](http://localhost/admin/)
проекта под логином и паролем администратора (пользователя, созданного командой createsuperuser).

---
## 6. Техническая информация <a id=6></a>

Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер backend)  
API фреймворк: Django REST (контейнер backend)  
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.  
Контейнер nginx взаимодействует с контейнером backend через gunicorn.  
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.

---
## 7. Об авторе <a id=7></a>

Бормотов Алексей Викторович  
Python-разработчик (Backend)  
Россия, г. Кемерово  
E-mail: di-devil@yandex.ru  
Telegram: @DIABLik666
