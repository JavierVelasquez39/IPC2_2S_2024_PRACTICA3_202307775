from django import forms

class FileForm(forms.Form):
    file = forms.FileField(label='Seleccione el archivo XML')