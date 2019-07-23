from django.conf import settings
from django.contrib import messages
import requests
import json
import hashlib
import re


MAILCHIMP_API_KEY = getattr(settings, "MAILCHIMP_API_KEY", None)
MAILCHIMP_DATA_CENTER = getattr(settings, "MAILCHIMP_DATA_CENTER", None)
MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)


def get_subscriber_hash(member_email):
    # check email
    member_email = member_email.lower().encode()
    m = hashlib.md5(member_email)
    return m.hexdigest()


def check_email(email):
    if not re.match(r".+@.+\..+", email):
        # raise ValueError("Passed string is not a valid email")
        return None
    return email.strip()


class Mailchimp(object):
    def __init__(self):
        super(Mailchimp, self).__init__()
        self.key = MAILCHIMP_API_KEY
        self.api_url = f"https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0"
        self.list_id = MAILCHIMP_EMAIL_LIST_ID
        self.list_endpoint = f'{self.api_url}/lists/{self.list_id}'
        self.members_endpoint = self.list_endpoint + "/members/"

    def check_subscription_status(self, email):
        hashed_email = get_subscriber_hash(email)

        endpoint = self.members_endpoint + hashed_email
        r = requests.get(endpoint, auth=("", self.key))
        return r.status_code, r.json()

    def change_subscription_status(self, email, status):
        hashed_email = get_subscriber_hash(email)

        data = {
            "email_address": email,
            "status": self.check_valid_status(status)
        }

        endpoint = self.members_endpoint + hashed_email
        r = requests.put(endpoint, auth=("", self.key), data=json.dumps(data))
        return r.status_code, r.json()

    def check_valid_status(self, status):
        choices = ['subscribed', 'unsubscribed', 'cleaned', 'pending']
        if status not in choices:
            raise ValueError("Not valid choice for email status")
        return status

    def unsubscribe(self, email):
        return self.change_subscription_status(email, status="unsubscribed")

    def subscribe(self, email):
        return self.change_subscription_status(email, status="subscribed")

    def pending(self, email):
        return self.change_subscription_status(email, status="pending")