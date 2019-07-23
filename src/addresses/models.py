from django.db import models
from billing.models import BillingProfile


ADDRESS_TYPES = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping')
)

class Address(models.Model):
    billing_profile     = models.ForeignKey(BillingProfile)
    address_type        = models.CharField(max_length=60, choices=ADDRESS_TYPES)
    company_name        = models.CharField(max_length=120, null=True, blank=True)
    name                = models.CharField(max_length=60, null=True)
    surname             = models.CharField(max_length=60, null=True)
    street              = models.CharField(max_length=60, null=True)
    home_number         = models.CharField(max_length=12, null=True)
    postal_code         = models.CharField(max_length=12, null=True)
    city                = models.CharField(max_length=60, null=True)
    country             = models.CharField(max_length=60, null=True, blank=True)
    phone               = models.CharField(max_length=20, null=True)
    current             = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}_{str(self.billing_profile)}_{self.address_type}"

    def print_address_html(self):
        address_list = [
            f"{self.name} {self.surname} {self.company_name or ''}",
            f"{self.street} {self.home_number}",
            f"{self.postal_code} {self.city} {self.country}",
            f"{self.phone}"
        ]
        return  address_list

    def print_address(self):
        return f"{self.name} {self.surname} {self.company_name or ''} \n {self.street} {self.home_number} \n{self.postal_code} {self.city} {self.country}\n{self.phone}"

    def make_stale(self):
        self.current = False
        self.save()