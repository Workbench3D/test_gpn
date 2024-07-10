from datetime import datetime, timedelta
from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            allowed_extensions = ["xlsx", "xls"]
            extension = file.name.split(".")[-1].lower()
            if extension not in allowed_extensions:
                raise forms.ValidationError("Загрузите файл формата excel(xlsx, xls)")
        return file


class DateRangeForm(forms.Form):
    now = datetime.now()
    delta = now - timedelta(days=360)

    start_date = forms.DateField(
        initial=delta.strftime("%Y-%m-%d"),
        widget=forms.TextInput(attrs={"type": "date"}),
    )
    end_date = forms.DateField(
        initial=now.strftime("%Y-%m-%d"),
        widget=forms.TextInput(attrs={"type": "date"}),
    )
