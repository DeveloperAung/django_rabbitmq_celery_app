from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import UserProfile, EmailTemplate
from django.conf import settings


@shared_task
def send_registration_notification(user_id):
    user = User.objects.get(id=user_id)
    managers = UserProfile.objects.filter(role='management')
    subject = 'New User Registration'
    message = f'A new user {user.username} has registered and is awaiting approval.'
    template = EmailTemplate.objects.filter(name='registration_notification').first()
    if template:
        subject = template.subject
        message = template.body.format(username=user.username)

    for manager in managers:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [manager.user.email],
            html_message=message if '<html>' in message else None,
        )
    # Simulated push notification (replace with actual push notification service)
    print(f"Push notification sent to managers for user: {user.username}")


@shared_task
def send_approval_status_email(user_id, is_approved):
    user = User.objects.get(id=user_id)
    template_name = 'approval_email' if is_approved else 'rejection_email'
    template = EmailTemplate.objects.filter(name=template_name).first()
    if template:
        subject = template.subject
        message = template.body.format(username=user.username)
    else:
        subject = 'Registration Status'
        message = f'Your registration has been {"approved" if is_approved else "rejected"}.'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message if '<html>' in message else None,
    )
