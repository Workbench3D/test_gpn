import pandas as pd
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UploadFileForm, DateRangeForm
from .models import Order


class FileHandler:
    """Класс для обработки файлов, чтения данных из Excel файла."""

    def __init__(self, file, sheet_name="Data"):
        self.file = file
        self.sheet_name = sheet_name

    def read_excel(self):
        return pd.read_excel(self.file, sheet_name=self.sheet_name)


class DataExtractor:
    """Класс для извлечения необходимых столбцов из DataFrame."""

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def extract_columns(self, *args):
        if args:
            self.dataframe = self.dataframe[list(args)]
        return self.dataframe


class DataTransformer:
    """Класс для преобразования данных из DataFrame в нужный формат."""

    @staticmethod
    def transform(data_list, idx_start_date, idx_end_date, idx_duration):
        for i in data_list:
            i[idx_start_date] = datetime.strptime(
                i[idx_start_date], "%d.%m.%Y %H:%M:%S"
            )
            if i[idx_end_date] is not None:
                i[idx_end_date] = datetime.strptime(
                    i[idx_end_date], "%d.%m.%Y %H:%M:%S"
                )
            if i[idx_duration] == "Обработка не завершена":
                i[idx_duration] = None
        return data_list


class OrderCreator:
    """Класс для создания объектов Order из списка данных."""

    @staticmethod
    def create_orders(data_list):
        return [
            Order(
                order_number=num,
                order_state=state,
                order_status=stat,
                order_author=author,
                creation_date=date,
                processing_end_date=end_date,
                processing_duration_hours=duration,
                package_id=id,
            )
            for num, state, stat, author, date, end_date, duration, id in data_list
        ]


def handle_uploaded_file(file, *args, sheet_name="Data"):
    file_handler = FileHandler(file, sheet_name)
    df = file_handler.read_excel().where(pd.notnull(file_handler.read_excel()), None)

    data_extractor = DataExtractor(df)
    df = data_extractor.extract_columns(*args)

    data_list = df.values.tolist()
    data_transformer = DataTransformer()
    return data_transformer.transform(
        data_list, idx_start_date=4, idx_end_date=5, idx_duration=6
    )


def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            download_data = handle_uploaded_file(
                file,
                "Номер заявки",
                "Состояние заявки",
                "Статус заявки",
                "Автор заявки",
                "Дата создания заявки",
                "Дата окончания обработки",
                "Время от создания заявки до конца обработки (в часах)",
                "ID пакета",
            )
            orders = OrderCreator.create_orders(download_data)
            Order.objects.bulk_create(orders)
            return redirect("index")
    else:
        form = UploadFileForm()
    return render(request, "reports/upload.html", {"form": form})


class OrderStatistics:
    """Класс для вычисления статистики по заявкам."""

    def __init__(self, orders):
        self.orders = orders

    def calculate(self):
        total_apps = self.orders.count()
        total_dups = self.orders.filter(order_state__contains="Дубликат заявки").count()
        new_apps = self.orders.filter(order_state__contains="ДОБАВЛЕНИЕ").count()
        extension_apps = self.orders.filter(order_state__contains="РАСШИРЕНИЕ").count()
        completed_apps = self.orders.filter(
            order_status__contains="Обработка завершена"
        ).count()
        returned_apps = self.orders.filter(
            order_status__contains="Возвращена на уточнение"
        ).count()
        processing_apps = self.orders.filter(
            order_status__contains="Отправлена в обработку"
        ).count()
        total_packages = self.orders.values("package_id").distinct().count()
        total_users = self.orders.values("order_author").distinct().count()

        return [
            total_apps,
            total_dups,
            new_apps,
            extension_apps,
            completed_apps,
            returned_apps,
            processing_apps,
            total_packages,
            total_users,
        ]


def get_orders(orders):
    order_statistics = OrderStatistics(orders)
    return order_statistics.calculate()


def get_report(request):
    now = datetime.now()
    delta = now - timedelta(days=360)

    orders = Order.objects.all()
    orders_date = orders.filter(creation_date__gte=delta, creation_date__lte=now)
    form = DateRangeForm(request.GET or None)

    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if start_date:
            orders_date = orders.filter(creation_date__gte=start_date)
        if end_date:
            orders_date = orders_date.filter(creation_date__lte=end_date)

    title = ["Название", "За указанный период", "За все время"]
    desc = [
        "Загруженных заявок",
        "Дубли",
        "На создание",
        "На расширение",
        "Обработка завершена",
        "Возвращена на уточнение",
        "Отправлена в обработку",
        "Пакетов",
        "Пользователей",
    ]
    content = zip(desc, get_orders(orders_date), get_orders(orders))
    context = {"title": title, "content": content}
    return render(request, "reports/report.html", {"form": form, "context": context})


def index(request) -> HttpResponse:
    return render(request, "reports/index.html")
