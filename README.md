To Do List + Выполняем проект по созданию календаря

Python3.10, Django, Postgres


1) Вводим poetry install
2) .env: 
SECRET_KEY = 'django-insecure-*^4$q$pne1(y2ijgzb@q(vayp=ia036o%a_emv-*2$9v@69gby'
DEBUG = True

DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=calendar_db
DB_USER=skypro
DB_PASSWORD=skypro
DB_HOST=localhost
DB_PORT=5432

DATABASE_URL = postgres://skypro:skypro@localhost:5432/calendar_db

3) calendar_postgres => docker-compose up
4) python manage.py migrate
5) python manage.py runserver