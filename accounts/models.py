# accounts/models.py
from django.db import models
import random
import string
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=20, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer-not-to-say', 'Prefer not to say')
    ], blank=True)
    faculty = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # 添加这行
    # 🔥 添加这两个计数字段
    items_sold = models.IntegerField(default=0)
    items_bought = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.student_id}"

    
    def __str__(self):
        return f"{self.user.username} - {self.student_id}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()