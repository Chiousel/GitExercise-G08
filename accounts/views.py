# accounts/views.py
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import PendingRegistration
import re

def index(request):
    """Home page"""
    return render(request, 'index.html')

def register_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        
        # Password confirmation check
        if password != confirm_password:
            messages.error(request, 'Password confirmation does not match')
            return redirect('register')
        
        # 1. Check if email is MMU email
        if not is_mmu_email(email):
            messages.error(request, 'Please use MMU campus email (@student.mmu.edu.my or @mmu.edu.my)')
            return redirect('register')
        
        # 2. Check if email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('register')
        
        # 3. Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('register')
        
        # 4. Create temporary registration record
        try:
            # Delete any existing old records
            PendingRegistration.objects.filter(email=email).delete()
            
            # Create new record
            pending_user = PendingRegistration(
                email=email,
                username=username,
                password=password  # Temporarily store plain text, will be encrypted after verification
            )
            pending_user.save()
            
            # 5. Send OTP email
            send_otp_email(email, pending_user.otp_code)
            
            # 6. Redirect to OTP verification page
            request.session['pending_email'] = email
            return redirect('verify_otp')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('register')
    
    # If GET request, show registration page
    return render(request, 'accounts/register.html')

def is_mmu_email(email):
    """
    Check if email is MMU email
    """
    mmu_domains = ['@student.mmu.edu.my', '@mmu.edu.my']
    return any(domain in email for domain in mmu_domains)

def send_otp_email(email, otp_code):
    """
    Send OTP email
    """
    subject = 'MMUBay - Email Verification Code'
    message = f'''
    Hello!
    
    Thank you for registering with MMUBay marketplace.
    Your verification code is: {otp_code}
    
    This code is valid for 30 minutes.
    If you did not request this code, please ignore this email.
    
    MMUBay Team
    '''
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, email_from, recipient_list)

def verify_otp(request):
    """
    Display and process OTP verification
    """
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        email = request.session.get('pending_email')
        
        if not email:
            messages.error(request, 'Session expired, please register again')
            return redirect('register')
        
        try:
            # Find temporary record
            pending_user = PendingRegistration.objects.get(email=email)
            
            # Check if OTP is expired
            if pending_user.is_expired():
                pending_user.delete()
                messages.error(request, 'Verification code expired, please register again')
                return redirect('register')
            
            # Check if OTP is correct
            if entered_otp == pending_user.otp_code:
                # OTP verification successful, create real user
                user = User.objects.create_user(
                    username=pending_user.username,
                    email=pending_user.email,
                    password=pending_user.password
                )
                user.save()
                
                # Delete temporary record
                pending_user.delete()
                
                # Clear session
                if 'pending_email' in request.session:
                    del request.session['pending_email']
                
                messages.success(request, 'Registration successful! Please login')
                return redirect('login')
            else:
                messages.error(request, 'Invalid verification code')
                return redirect('verify_otp')
                
        except PendingRegistration.DoesNotExist:
            messages.error(request, 'Session expired, please register again')
            return redirect('register')
    
    return render(request, 'accounts/otp_verification.html')

def login_view(request):
    """
    Handle user login
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check required fields
        if not email or not password:
            messages.error(request, 'Please enter both email and password')
            return redirect('login')
        
        # Try to find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
        
        # Verify user password
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
    
    # If GET request, show login page
    return render(request, 'accounts/login.html')

def test_email(request):
    """Test email sending functionality"""
    try:
        send_mail(
            'Test Email - MMUBay',
            'This is a test email! If you receive this, email configuration is working!',
            settings.EMAIL_HOST_USER,
            ['SO.DHE.WEI@student.mmu.edu.my'],
            fail_silently=False,
        )
        return HttpResponse('Test email sent successfully! Please check your email (including spam folder).')
    except Exception as e:
        return HttpResponse(f'Email sending failed: {str(e)}')