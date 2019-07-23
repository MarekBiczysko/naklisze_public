from django.contrib import admin
from .models import MarketingPref


class MarketingPrefAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'subscribed']

    readonly_fields = [
        'mailchimp_subscribed',
        'timestamp',
        'updated',
        'mailchimp_msg'
        ]
    class Meta:
        model = MarketingPref
        fields = [
            'user',
            'subscribed',
            'mailchimp_msg',
            'mailchimp_subscribed',
            'timestamp',
            'updated'
        ]

admin.site.register(MarketingPref, MarketingPrefAdmin)