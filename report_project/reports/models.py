from django.db import models
from django.utils import timezone


class Order(models.Model):
    order_number = models.CharField(max_length=100, verbose_name="Номер заявки")
    order_status = models.CharField(max_length=100, verbose_name="Состояние заявки")
    approval = models.CharField(max_length=100, verbose_name="Согласование")
    order_author = models.CharField(max_length=100, verbose_name="Автор заявки")
    creation_date = models.DateTimeField(verbose_name="Дата создания заявки")
    processing_end_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата окончания обработки"
    )
    processing_duration_hours = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Время от создания заявки до конца обработки (в часах)",
    )
    package_id = models.CharField(max_length=100, verbose_name="ID пакета")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return self.order_number
