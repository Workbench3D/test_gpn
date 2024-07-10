from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime, timedelta

from django.urls import reverse

from .forms import UploadFileForm, DateRangeForm


class FormsTest(TestCase):
    def test_upload_file_form_valid(self):
        # Тестирование с правильным форматом файла
        file = SimpleUploadedFile(
            "test.xlsx",
            b"file_content",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        form = UploadFileForm(files={"file": file})
        self.assertTrue(form.is_valid())

    def test_upload_file_form_invalid_extension(self):
        # Тестирование с неправильным форматом файла
        file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )
        form = UploadFileForm(files={"file": file})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["file"], ["Загрузите файл формата excel(xlsx, xls)"]
        )

    def test_date_range_form_valid(self):
        # Тестирование с корректным диапазоном дат
        now = datetime.now()
        delta = now - timedelta(days=360)
        form_data = {
            "start_date": delta.strftime("%Y-%m-%d"),
            "end_date": now.strftime("%Y-%m-%d"),
        }
        form = DateRangeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_date_range_form_initial_values(self):
        # Тестирование начальных значений формы
        form = DateRangeForm()
        now = datetime.now().strftime("%Y-%m-%d")
        delta = (datetime.now() - timedelta(days=360)).strftime("%Y-%m-%d")
        self.assertEqual(form.fields["start_date"].initial, delta)
        self.assertEqual(form.fields["end_date"].initial, now)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/index.html")

    def test_upload_file_view_get(self):
        response = self.client.get(reverse("upload_file"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/upload.html")
        self.assertIsInstance(response.context["form"], UploadFileForm)

    def test_upload_file_view_post_invalid_extension(self):
        file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )
        response = self.client.post(reverse("upload_file"), {"file": file})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/upload.html")
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())
