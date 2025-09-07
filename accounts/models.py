# accounts/models.py
from django.db import models
import random
import string
from django.utils import timezone

def generate_otp():
    """生成一个6位的随机数字OTP"""
    return ''.join(random.choices(string.digits, k=6))

class PendingRegistration(models.Model):
    email = models.EmailField(unique=True)
    otp_code = models.CharField(max_length=6, default=generate_otp)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)  # 存储加密后的密码
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        """检查OTP是否已过期（30分钟）"""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=30)
    
    def __str__(self):
        return f"{self.email} - {self.otp_code} (Expires: {self.created_at + timezone.timedelta(minutes=30)})"