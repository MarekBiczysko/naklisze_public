from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils import six  # Python 3 compatibility
from django.utils.functional import lazy


mark_safe_lazy = lazy(mark_safe, six.text_type)

User = get_user_model()

newsletter_accept_txt = _("<small>„Wyrażam zgodę na przetwarzanie moich danych osobowych w rozumieniu ustawy z dnia 29 sierpnia 1997 roku o ochronie danych osobowych oraz ustawy z dnia 16 lipca 2004 roku Prawo telekomunikacyjne w celach marketingowych przez Marek Biczysko – naklisze.pl i oświadczam, iż podanie przeze mnie danych osobowych jest dobrowolne oraz iż zostałem poinformowany o prawie żądania dostępu do moich danych osobowych, ich zmiany oraz usunięcia. Wyrażam zgodę na otrzymywanie drogą elektroniczną na wskazany przeze mnie adres e-mail informacji handlowej w rozumieniu art. 10 ust. 1 ustawy z dnia 18 lipca 2002 roku o świadczeniu usług drogą elektroniczną.“</small>")
account_accept_txt = _("<small>„Oświadczam, iż ukończyłam/em 16 rok życia i zgadzam się na przetwarzanie moich danych osobowych przez Marek Biczysko - naklisze.pl, w celu prowadzenia konta w sklepie. Podanie danych jest dobrowolne. Podstawą przetwarzania danych jest moja zgoda. Mam prawo wycofania zgody w dowolnym momencie. Dane osobowe będą przetwarzane do czasu odwołania zgody. Mam prawo żądania od administratora dostępu do moich danych osobowych, ich sprostowania, usunięcia lub ograniczenia przetwarzania, a także prawo wniesienia skargi do organu nadzorczego. Strona stosuje profilowanie użytkowników m.in. za pośrednictwem plików cookies, w tym analitycznych, o czym więcej w Polityce Prywatności.”</small><hr>")

class UserDataUpdateForm(forms.ModelForm):
    username = forms.CharField(
        label=_('Nazwa użytkownika'),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }),
            required=False
    )

    class Meta:
        model = User
        fields = ['username',]


class GuestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "E-Mail",
            }
        ),
        label=_("Twój E-Mail")
    )

    subscribe = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "style": "width: 15px; height: 15px; margin: 5px 6px 6px;"
            }
        ),
        label=_("Subskrypcja newslettera"),
        help_text=mark_safe_lazy(newsletter_accept_txt)

    )


class LoginForm(forms.Form):
    username = forms.CharField(
        label=_("Twój Login"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Login",
            }))

    password = forms.CharField(
        label=_("Twoje hasło"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Hasło"),
                }),
               help_text=mark_safe_lazy(
                   """
                  <small id="password-caps-warning" class="form-text text-warning pr-3 d-none">Caps lock!</small>
                   """)
                )

    def clean_username(self):
        data = self.cleaned_data
        username = data.get('username')
        qs = User.objects.filter(username=username)
        if not qs.exists():
            raise forms.ValidationError(_("Niepoprawny użytkownik"))
        return username


class RegisterForm(forms.Form):
    username = forms.CharField(
        label=_("Twój Login"),
        widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": _("Nazwa"),
        }))

    password = forms.CharField(
        label=_("Twoje hasło"),
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": _("Hasło"),
        }),
        help_text=mark_safe_lazy(
            """
           <small id="password-caps-warning" class="form-text text-warning pr-3 d-none">Caps lock!</small>
            """)
    )

    password2 = forms.CharField(
        label=_("Potwierdź hasło"),
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": _("Hasło"),
        }),
        help_text = mark_safe_lazy(
            """
           <small id="password-caps-warning" class="form-text text-warning pr-3 d-none">Caps lock!</small>
            """)
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "E-Mail",
            }
        ),
        label=_("Twój E-Mail")
    )

    accept = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "style": "width: 15px; height: 15px; margin: 5px 6px 6px;"
            }
        ),
        label=_("Akceptuję poniższą zgodę"),
        help_text=mark_safe_lazy(account_accept_txt)
        )

    subscribe = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "style": "width: 15px; height: 15px; margin: 5px 6px 6px;"
            }
        ),
        label=_("Subskrypcja newslettera"),
        help_text=mark_safe_lazy(newsletter_accept_txt)
    )


    def clean_username(self):
        data = self.cleaned_data
        username = data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError(_("Użytkownik już istnieje"))
        return username

    def clean_password2(self):
        data = self.cleaned_data
        password = data.get('password')
        password2 = data.get('password2')
        if password2 != password:
            raise forms.ValidationError(_("Niezgodność podanych haseł"))
        return password2

    def clean_email(self):
        data = self.cleaned_data
        email = data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError(_("Email znajduje się już w bazie"))
        return email
