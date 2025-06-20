from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('email-logs/', views.email_log_view, name='email_log'),
]
