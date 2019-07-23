from django import forms
from .models import Address
from django.utils.translation import ugettext_lazy as _


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            # 'billing_profile',
            # 'address_type',
            'company_name',
            'name',
            'surname',
            'street',
            'home_number',
            'postal_code',
            'city',
            'country',
            'phone'
            ]

        widgets = {
            'name': forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("* Imię"),
            }),
            'surname': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Nazwisko"),
                }),
            'company_name': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Nazwa firmy"),
                }),
            'street': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Ulica"),
                }),
            'home_number': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Nr domu/mieszkania"),
                }),
            'postal_code': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Kod pocztowy"),
                }),
            'city': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Miasto"),
                }),
            'country': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Kraj"),
                }),
            'phone': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("* Nr telefonu"),
                }),

        }
        labels = {
            'name': _('Imię'),
            'surname': _('Nazwisko'),
            'company_name': _('Nazwa firmy'),
            'street': _('Ulica'),
            'home_number': _('Nr domu/mieszkania'),
            'postal_code': _('Kod pocztowy'),
            'city': _('Miasto'),
            'country': _('Kraj'),
            'phone': _('Nr telefonu'),

        }
