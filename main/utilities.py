from django.template.loader import render_to_string
from django.core.signing import Signer
from datetime import datetime
from os.path import splitext

from callboard.settings import ALLOWED_HOSTS


signer = Signer()


def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    context = {'user': user, 'host': host, 'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    '''функция генерирующая имена картинок. splitext(filename) - оставит только имя файла, без расширения,
    datetime.now().timestamp()-прикрепит дату и время в имя файла. '''
    return f'{datetime.now().timestamp()},{splitext(filename)}'


