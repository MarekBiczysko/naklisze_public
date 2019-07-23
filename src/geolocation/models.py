import requests
import re

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.utils.datetime_safe import datetime

from analytics.models import ObjectViewed

User = settings.AUTH_USER_MODEL
GEO_API_URL = 'http://api.ipstack.com/'
KEY_URL = '?access_key=f47cb89c519c5bc3da3f570c2847652e'


class GeolocationManager(models.Manager):

    def create_if_new(self, ip, viewed_object, user=None):
        obj, created = self.update_or_create(ip=ip, user=user, defaults=
        {
            'date': datetime.now(),
            'viewed_object': viewed_object
        }
                                             )
        if created:
            obj.fill_geo_data()


class Geolocation(models.Model):
    user            = models.ForeignKey(User, blank=True, null=True) # User instance
    ip              = models.CharField(max_length=120, null=True, blank=True)
    country_code    = models.CharField(max_length=120, null=True, blank=True)
    country_name    = models.CharField(max_length=120, null=True, blank=True)
    region_code     = models.CharField(max_length=120, null=True, blank=True)
    region_name     = models.CharField(max_length=120, null=True, blank=True)
    city            = models.CharField(max_length=120, null=True, blank=True)
    zip_code        = models.CharField(max_length=120, null=True, blank=True)
    latitude        = models.CharField(max_length=120, null=True, blank=True)
    longitude       = models.CharField(max_length=120, null=True, blank=True)
    viewed_object   = models.CharField(max_length=200, null=True, blank=True)
    date            = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    objects = GeolocationManager()

    def fill_geo_data(self):
        geodata = get_geo_by_ip(self.ip)
        if geodata:
            self.ip = geodata.get('ip')
            self.country_code = geodata.get('country_code')
            self.country_name = geodata.get('country_name')
            self.region_code = geodata.get('region_code')
            self.region_name = geodata.get('region_name')
            self.city = geodata.get('city')
            self.zip_code = geodata.get('zip_code')
            self.latitude = geodata.get('latitude')
            self.longitude = geodata.get('longitude')
            self.save()

    def print_geo_data(self):
        return f"IP: {self.ip}, Country: {self.country_code}, CountryName: {self.country_name}, " \
               f"RegionCode: {self.region_code}, RegionName: {self.region_name}, City: {self.city}, " \
               f"ZipCode: {self.zip_code}, Latitude: {self.latitude}, Longitude: {self.longitude}"


def get_geo_by_ip(ip):
    geodata = None
    resp = requests.get(GEO_API_URL + f'{ip}' + KEY_URL)
    if resp.status_code == 200:  # SUCCESS
        geodata = resp.json()
    return geodata


def validate_ipv4(ip):
    match = re.match(r'\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b', ip)
    return True if match else False


def object_viewed_post_save_receiver(sender, instance, *args, **kwargs):
    if not kwargs.get('raw', False):
        Geolocation.objects.create_if_new(ip=instance.ip_address, user=instance.user, viewed_object=str(instance.content_object))

post_save.connect(object_viewed_post_save_receiver, sender=ObjectViewed)
