# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_request, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('test-email/', views.test_email, name='test_email'),
    path('login/', views.login_view, name='login'),  # ← 添加这一行！
]