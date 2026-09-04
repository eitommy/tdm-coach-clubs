from django import forms

from .models import Club


class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = [
            "nombre",
            "logo",
            "color_primario",
            "color_secundario",
            "email",
            "telefono",
            "direccion",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "direccion": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "color_primario": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color",
            }),
            "color_secundario": forms.TextInput(attrs={
                "type": "color",
                "class": "form-control form-control-color",
            }),
        }