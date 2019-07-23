from modeltranslation.translator import register, translator, TranslationOptions
from .models import Infobox


@register(Infobox)
class ProductTranslationOptions(TranslationOptions):
    fields = ('message',)

