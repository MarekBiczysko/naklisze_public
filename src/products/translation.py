from modeltranslation.translator import register, translator, TranslationOptions
from .models import Product, Camera, Strap, Button


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Camera)
class CameraTranslationOptions(TranslationOptions):
    fields = ('set_description', 'description', 'spec_table',)

@register(Strap)
class StrapTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(Button)
class ButtonTranslationOptions(TranslationOptions):
    fields = ('description',)
