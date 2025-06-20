from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import UserProfile, EmailTemplate, EmailLog
from django.conf import settings
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def send_registration_notification(self, user_id):
    try:
        user = User.objects.get(id=user_id)
        managers = UserProfile.objects.filter(role='management')
        subject = 'New User Registration'
        message = f'A new user {user.username} has registered and is awaiting approval.'
        template = EmailTemplate.objects.filter(name='registration_notification').first()
        if template:
            subject = template.subject
            message = template.body.format(username=user.username)

        # Create email log entry
        for manager in managers:
            email_log = EmailLog.objects.create(
                recipient=manager.user,
                subject=subject,
                body=message,
                status='pending',
                task_id=self.request.id
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [manager.user.email],
                    html_message=message if '<html>' in message else None,
                    fail_silently=False,
                )
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
                email_log.save()
                # Simulated push notification
                print(f"Push notification sent to {manager.user.username} for user: {user.username}")
            except Exception as e:
                email_log.status = 'failed'
                email_log.error_message = str(e)
                email_log.save()
                # Retry on failure
                raise self.retry(exc=e, countdown=60)

    except MaxRetriesExceededError:
        email_log.status = 'failed'
        email_log.error_message = 'Max retries exceeded'
        email_log.save()
        raise


@shared_task(bind=True, max_retries=3)
def send_approval_status_email(self, user_id, is_approved):
    try:
        user = User.objects.get(id=user_id)
        template_name = 'approval_email' if is_approved else 'rejection_email'
        template = EmailTemplate.objects.filter(name=template_name).first()
        if template:
            subject = template.subject
            message = template.body.format(username=user.username)
        else:
            subject = 'Registration Status'
            message = f'Your registration has been {"approved" if is_approved else "rejected"}.'

        # Create email log entry
        email_log = EmailLog.objects.create(
            recipient=user,
            subject=subject,
            body=message,
            status='pending',
            task_id=self.request.id
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message if '<html>' in message else None,
                fail_silently=False,
            )
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.save()
        except Exception as e:
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save()
            raise self.retry(exc=e, countdown=60)

    except MaxRetriesExceededError:
        email_log.status = 'failed'
        email_log.error_message = 'Max retries exceeded'
        email_log.save()
        raise
