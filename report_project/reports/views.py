from datetime import datetime, timedelta
from django.http import HttpResponse
import pandas as pd

from .models import Order

from .forms import UploadFileForm, DateRangeForm
from django.shortcuts import render, redirect


def index(request) -> HttpResponse:
    return render(request, "reports/index.html")


def handle_uploaded_file(file, *args, sheet_name="Data") -> list:
    """
    Читает определенные столбцы из Excel файла и формирует из них список.

    :file: загруженый Excel файл
    :sheet_name: имя листа
    :args: названия столбцов для выбора
    """
    # Читаем данные с указанного листа Excel файла
    df = pd.read_excel(file, sheet_name=sheet_name)
    df = df.where(pd.notnull(df), None)

    # Если указаны столбцы, выбираем их
    if args:
        df = df[list(args)]

    # Преобразуем данные DataFrame в список списков
    data_list = df.values.tolist()
    for i in data_list:
        i[4] = datetime.strptime(i[4], "%d.%m.%Y %H:%M:%S")
        if i[5] is not None:
            i[5] = datetime.strptime(i[5], "%d.%m.%Y %H:%M:%S")
        if i[6] == "Обработка не завершена":
            i[6] = None
    return data_list


def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            dowload_data = handle_uploaded_file(
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
            order = [
                Order(
                    order_number=i[0],
                    order_state=i[1],
                    order_status=i[2],
                    order_author=i[3],
                    creation_date=i[4],
                    processing_end_date=i[5],
                    processing_duration_hours=i[6],
                    package_id=i[7],
                )
                for i in dowload_data
            ]
            Order.objects.bulk_create(order)
            return redirect("index")
    else:
        form = UploadFileForm()
    return render(request, "reports/upload.html", {"form": form})


def get_orders(orders: Order) -> dict:
    total_apps = orders.count()
    total_dups = orders.filter(order_state__contains="Дубликат заявки").count()
    new_apps = orders.filter(order_state__contains="ДОБАВЛЕНИЕ").count()
    extension_apps = orders.filter(order_state__contains="РАСШИРЕНИЕ").count()
    completed_apps = orders.filter(order_status__contains="Обработка завершена").count()
    returned_apps = orders.filter(
        order_status__contains="Возвращена на уточнение"
    ).count()
    processing_apps = orders.filter(
        order_status__contains="Отправлена в обработку"
    ).count()
    total_packages = orders.values("package_id").distinct().count()
    total_users = orders.values("order_author").distinct().count()

    result = [
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
    return result


def get_report(request) -> HttpResponse:
    now = datetime.now()
    delta = now - timedelta(days=360)

    orders = Order.objects.all()
    orders_date = orders.filter(creation_date__gte=delta)
    orders_date = orders_date.filter(creation_date__lte=now)
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
