from django.db import models


class Infobox(models.Model):
    message     = models.TextField(max_length=500, null=True, blank=True)
    active      = models.BooleanField(default=False)

