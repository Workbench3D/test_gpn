from datetime import datetime
from django.http import HttpResponse
import pandas as pd

from .models import Order

from .forms import UploadFileForm
from django.shortcuts import render, redirect
from django.contrib import messages


def index(request):
    return HttpResponse("index")


def handle_uploaded_file(file, *args, sheet_name="Data"):
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
                "Согласование",
                "Автор заявки",
                "Дата создания заявки",
                "Дата окончания обработки",
                "Время от создания заявки до конца обработки (в часах)",
                "ID пакета",
            )
            order = [
                Order(
                    order_number=i[0],
                    order_status=i[1],
                    approval=i[2],
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
