from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, ApprovalForm
from .models import UserProfile
from .tasks import send_registration_notification, send_approval_status_email


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, phone_number=form.cleaned_data['phone_number'])
            send_registration_notification.delay(user.id)
            messages.success(request, 'Registration successful. Awaiting approval.')
            return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration_form.html', {'form': form})


@login_required
def approve_user(request, user_id):
    if not request.user.profile.role == 'management':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid():
            is_approved = form.cleaned_data['is_approved']
            user.profile.is_approved = is_approved
            user.profile.save()
            send_approval_status_email.delay(user.id, is_approved)
            messages.success(request, f'User {user.username} has been {"approved" if is_approved else "rejected"}.')
            return redirect('approve_user', user_id=user.id)
    else:
        form = ApprovalForm()
    return render(request, 'approval_form.html', {'form': form, 'user': user})
