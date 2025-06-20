from django.contrib import admin
from .models import UserProfile, EmailTemplate, EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'recipient')
    search_fields = ('recipient__username', 'subject')
    readonly_fields = ('created_at', 'sent_at', 'error_message', 'task_id')


admin.site.register(UserProfile)
admin.site.register(EmailTemplate)
