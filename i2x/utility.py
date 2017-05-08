import re
from random import choice
from string import ascii_uppercase
from django.core.mail import send_mail
from smtplib import SMTPException
from django.template.loader import get_template
from django.conf import settings

# below regex is good for 90% cases - to achieve 100% go below
# http://stackoverflow.com/questions/201323/using-a-regular-expression-to-validate-an-email-address
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def is_valid_email(email):
    if not EMAIL_REGEX.match(email):
        return False
    return True


def get_random_code(code_length=10):
    """
    Generates the random code
    :param code_length: set the code length
    :return: randomized the code length
    """
    return ''.join(choice(ascii_uppercase) for i in range(code_length))


def send_registration_mail(username, email, code):
    subject = settings.REGISTRATION_EMAIL['SUBJECT']
    from_email = settings.EMAIL_HOST_USER
    recipient = email

    email_context = {
        'username': username,
        'code': code,
        'verification_link': settings.BASE_WEBSITE_URL + "/verify?code=" + code
    }

    message = get_template('registration.html').render(email_context)

    try:
        send_mail(subject, message, from_email, [recipient], fail_silently=False)
    except SMTPException as e:
        return False

    return True
