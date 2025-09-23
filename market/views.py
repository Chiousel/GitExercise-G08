from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Item, ItemImage
from .forms import ItemForm, ItemImageForm
from django.contrib.auth.models import User
from .models import Item  # 假设您有Item模型
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def item_list(request):
    query = request.GET.get('q')
    items = Item.objects.filter(is_sold=False).order_by('-created_at')
    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))
    
    return render(request, 'market/item_list.html', {
        'items': items,
        'user': request.user,  # 添加用户信息
        'is_authenticated': request.user.is_authenticated  # 添加认证状态
    })


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'market/item_detail.html', {'item': item})

@login_required  # 添加这个装饰器
@require_POST
def change_password(request):
    if request.method == 'POST':
        # 使用Django的PasswordChangeForm，它期望特定的字段名
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # 更新会话认证哈希，避免用户被登出
            update_session_auth_hash(request, user)
            return JsonResponse({'success': True, 'message': 'Password updated successfully!'})
        else:
            # 更好的错误处理
            errors = []
            for field, error_list in form.errors.items():
                for error in error_list:
                    errors.append(str(error))
            return JsonResponse({'success': False, 'error': ' '.join(errors)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        files = request.FILES.getlist('images')  # multiple files
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()

            # Save uploaded images
            for f in files:
                ItemImage.objects.create(item=item, image=f)

            return redirect('item_detail', item_id=item.id)
    else:
        form = ItemForm()
    return render(request, 'market/item_form.html', {'form': form})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        files = request.FILES.getlist('images')
        if form.is_valid():
            form.save()

            # Add new uploaded images
            for f in files:
                ItemImage.objects.create(item=item, image=f)

            return redirect('item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'market/item_form.html', {'form': form, 'item': item})


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'market/confirm_delete.html', {'item': item})

@login_required
def delete_image(request, image_id):
    from .models import ItemImage
    image = get_object_or_404(ItemImage, id=image_id)

    # Ensure only the item owner can delete
    if image.item.seller != request.user:
        return redirect('item_detail', item_id=image.item.id)

    if request.method == 'POST':
        image.delete()
        return redirect('edit_item', item_id=image.item.id)

    return render(request, 'market/confirm_delete_image.html', {'image': image})

@login_required
def profile(request):
    if request.method == 'POST':
        # 处理表单提交
        user = request.user
        user.first_name = request.POST.get('firstName', '')
        user.last_name = request.POST.get('lastName', '')
        user.save()
        
        # 更新用户配置
        profile = user.userprofile
        profile.phone_number = request.POST.get('phone', '')
        profile.gender = request.POST.get('gender', '')
        profile.faculty = request.POST.get('faculty', '')
        profile.bio = request.POST.get('bio', '')
        profile.student_id = request.POST.get('studentId', '')  # 添加这行
        # 处理头像上传
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        
        return redirect('profile')
    
    user = request.user
    
    # 获取真实的统计数据
    items_sold = Item.objects.filter(seller=user, is_sold=True).count()
    try:
        items_bought = Item.objects.filter(buyer=user).count()
    except:
        items_bought = 0  # 如果没有buyer字段，先设为0
    
    context = {
        'user': user,
        'profile': user.userprofile,  # 添加用户配置
        'items_sold': items_sold,
        'items_bought': items_bought,
        'rating': 0,
    }
    return render(request, 'profile.html', context)

def view_profile(request, username):
    """查看用户的公开资料"""
    try:
        profile_user = get_object_or_404(User, username=username)
        
        # 确保用户有userprofile
        if not hasattr(profile_user, 'userprofile'):
            from accounts.models import UserProfile
            UserProfile.objects.create(user=profile_user, student_id=f"STD{profile_user.id:06d}")
        
        items = Item.objects.filter(seller=profile_user, is_sold=False)
        items_sold = Item.objects.filter(seller=profile_user, is_sold=True).count()
        
        context = {
            'profile_user': profile_user,
            'items': items,
            'items_count': items.count(),
            'items_sold': items_sold, 
            'rating': 0,  # 初始评分设为0
            'is_own_profile': request.user == profile_user,
        }
        return render(request, 'market/public_profile.html', context)
    
    except Exception as e:
        # 如果出错，重定向回个人资料页
        return redirect('profile')
# Create your views here.