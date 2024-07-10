# Сервис отчетов
Сервис формирования отчетов.

Принимает excel файл у которого должна быть страница Data, также на этой странице, должны быть столбцы: 
- Номер заявки
- Состояние заявки
- Статус заявки
- Автор заявки
- Дата создания заявки
- Дата окончания обработки
- Время от создания заявки до конца обработки (в часах)
- ID пакета

## Стек

#### Прод
- Python - 3.10.12
- Postgres - 14.7
- Django - 4.2.13
- Psycopg2 - 2.9.9
- Pandas - 2.2.2

#### Разработка
- Линтер: Ruff - 0.5.1
- Покрытие тестами: Coverage - 7.5.4

Покрытие тестами 70%

## Структура проекта

```bash
├── docker-compose.yaml
├── Dockerfile
├── README.md
├── report_project
│   ├── manage.py
│   ├── .env
│   ├── report_project
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── reports
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── migrations
│       │   ├── 0001_initial.py
│       │   └── __init__.py
│       ├── models.py
│       ├── static
│       │   └── bootstrap-5.2.3
│       ├── templates
│       │   ├── layout
│       │   └── reports
│       ├── tests.py
│       ├── urls.py
│       └── views.py
└── requirements
    ├── dev.txt
    └── prod.txt
```

## Разворачивание сервиса

Сервис состоит из двух докер контейнеров.

Создать **.env** файл в директроии `./report_project`

#### env файл

```
# Переменная окружения для сервиса Django
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
SECRET_KEY=django секретный ключ
DB_HOST=db
DB_PORT=5432

# Переменная окружения для сервиса db (PosgreSQL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_DB=reports
POSTGRES_PORT=5432
DATA_PATH=директория куда пробросить хранилище
```

Запустить сборку контейнера с команды `docker-compose --env-file report_project/.env up -d`.

Запустить миграцию базы данных командой `docker exec -it reports python report_project/manage.py migrate`.

Возможно потребуется перезагрузить контейнер с Django, команда `docker restart reports`.
