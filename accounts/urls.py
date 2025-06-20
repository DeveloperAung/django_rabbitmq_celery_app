from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('approve/<int:user_id>/', views.approve_user, name='approve_user'),
]
