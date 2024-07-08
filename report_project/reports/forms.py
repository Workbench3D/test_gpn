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
