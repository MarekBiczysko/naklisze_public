from django.contrib import admin
from modeltranslation.admin import TranslationAdmin


from .models import Infobox

class InfoboxAdmin(admin.ModelAdmin):
    list_display = ['message', 'active']


@admin.register(Infobox)
class MyTranslatedProductAdmin(InfoboxAdmin, TranslationAdmin):
    pass
