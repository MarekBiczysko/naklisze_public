from django.utils.text import slugify
import random
import string
from time import strftime, gmtime

from sklep.log import loger


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug

def date_generator():
    return strftime("%y%m%d", gmtime())

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def uniqe_order_id_generator(instance):

    new_order_id = "{date}/{randstr}".format(
                    date=date_generator(),
                    randstr=random_string_generator(size=4)
                )

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=new_order_id).exists()
    if qs_exists:
        return uniqe_order_id_generator(instance)
    return new_order_id


import threading
from django.core.mail import EmailMessage

class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list, attachments):
        self.subject = subject
        self.recipient_list = recipient_list
        self.message = message
        self.attachments = [attachments] if not isinstance(attachments, list) else attachments
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.message, to=self.recipient_list)

        for att in self.attachments:
            msg.attach_file(att)
        msg.content_subtype = 'html'

        msg.send()
        loger.info(f'Email  with subject {self.subject} was successfuly send to {self.recipient_list}')


def send_mail(subject, message, recipient_list, attachments):
    EmailThread(subject, message, recipient_list, attachments).start()

