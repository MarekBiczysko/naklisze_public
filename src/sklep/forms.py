from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils import six  # Python 3 compatibility
from django.utils.functional import lazy

mark_safe_lazy = lazy(mark_safe, six.text_type)
accept_help_text = _("<small>„Oświadczam, iż ukończyłam/em 16 rok życia i zgadzam się na przetwarzanie moich danych osobowych przez Marek Biczysko - naklisze.pl, w celu obsługi zapytania użytkownika. Podanie danych jest dobrowolne. Podstawą przetwarzania danych jest moja zgoda. Mam prawo wycofania zgody w dowolnym momencie. Dane osobowe będą przetwarzane do czasu obsługi zapytania. Mam prawo żądania od administratora dostępu do moich danych osobowych, ich sprostowania, usunięcia lub ograniczenia przetwarzania, a także prawo wniesienia skargi do organu nadzorczego. Strona stosuje profilowanie użytkowników m.in. za pośrednictwem plików cookies, w tym analitycznych, o czym więcej w Polityce Prywatności.”</small>")


class ContactForm(forms.Form):
    fullname = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Twoje imię i nazwisko"),
            }
        ),
        label=_("Dane kontaktowe")
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Twój E-Mail"),
            }
        ),
        label=_("E-Mail")
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": _("Treść wiadomości")
            }
        ),
        label=_("Treść wiadomości")
    )
    accept = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "style": "width: 15px; height: 15px; margin: 5px 6px 6px;"
            }
        ),
        label=_("Akceptuję poniższą zgodę"),
        help_text= mark_safe_lazy(accept_help_text)
    )
