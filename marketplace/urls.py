"""
URL configuration for marketplace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# marketplace/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from accounts import views  # 添加这行导入

def redirect_to_index(request):
    return redirect('index')  # 这将重定向到首页

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # 包含accounts应用的URL
    path('', views.index, name='index'),  # 首页路由
]
