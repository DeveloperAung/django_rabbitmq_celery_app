from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('management', 'Management'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EmailLog(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    task_id = models.CharField(max_length=100, blank=True, null=True)  # Store Celery task ID

    def __str__(self):
        return f"{self.recipient.username} - {self.subject} - {self.status}"

    class Meta:
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"
