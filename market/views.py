from django.contrib import messages  # 添加这行
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Order
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
        items = items.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(category__icontains=query)
        )
    
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
        # 获取来源页面参数
        next_url = request.POST.get('next', 'my_items')
        
        # 删除商品
        item_title = item.title
        item.delete()
        
        messages.success(request, f'Item "{item_title}" has been deleted successfully!')
        
        # 根据来源决定跳转
        if next_url == 'item_list':
            return redirect('item_list')
        else:
            return redirect('my_items')
    
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
    
    # 🔥 修复：从Order模型获取购买数量
    items_bought = Order.objects.filter(buyer=user, status='completed').count()
    
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
        # 🔥 修复：使用UserProfile的统计字段
        items_sold = profile_user.userprofile.items_sold
        items_bought = profile_user.userprofile.items_bought
        
        context = {
            'profile_user': profile_user,
            'items': items,
            'items_count': items.count(),
            'items_sold': items_sold, 
            'items_bought': items_bought,  # 新增购买统计
            'rating': 0,  # 初始评分设为0
            'is_own_profile': request.user == profile_user,
        }
        return render(request, 'market/public_profile.html', context)
    
    except Exception as e:
        # 如果出错，重定向回个人资料页
        return redirect('profile')

@login_required
def my_items(request):
    # 处理标记售出
    if request.method == 'POST' and 'mark_sold' in request.POST:
        item_id = request.POST.get('mark_sold')
        if item_id:
            try:
                item = Item.objects.get(id=item_id, seller=request.user)
                item.is_sold = True
                item.save()
                messages.success(request, f'"{item.title}" has been marked as sold!')
                return redirect('my_items')
            except Item.DoesNotExist:
                messages.error(request, 'Item not found!')
    
    # 获取用户商品
    active_items = Item.objects.filter(seller=request.user, is_sold=False).order_by('-created_at')
    sold_items = Item.objects.filter(seller=request.user, is_sold=True).order_by('-created_at')
    
    # 获取待处理订单
    pending_orders = Order.objects.filter(seller=request.user, status='pending').order_by('-created_at')  # 这行定义变量
    pending_orders_count = pending_orders.count()
    
    return render(request, 'market/my_items.html', {
        'active_items': active_items,
        'sold_items': sold_items,
        'pending_orders': pending_orders,  # 新增：传递订单数据
        'pending_orders_count': pending_orders_count  # 新增
    })

@login_required
def place_order(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # 检查商品是否已售出
    if item.is_sold:
        messages.error(request, 'This item has already been sold!')
        return redirect('item_detail', item_id=item_id)
    
    # 检查用户是否在买自己的商品
    if item.seller == request.user:
        messages.error(request, 'You cannot place an order for your own item!')
        return redirect('item_detail', item_id=item_id)
    
    # 检查是否已经下过订单
    existing_order = Order.objects.filter(item=item, buyer=request.user).first()
    if existing_order:
        messages.info(request, 'You have already placed an order for this item!')
        return redirect('item_detail', item_id=item_id)
    
    # 创建新订单
    if request.method == 'POST':
        order = Order.objects.create(
            item=item,
            buyer=request.user,
            seller=item.seller,
            status='pending'
        )
        
        messages.success(request, f'Order placed successfully! {item.seller.username} will contact you soon.')
        return redirect('item_detail', item_id=item_id)
    
    return redirect('item_detail', item_id=item_id)

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    
    if request.method == 'POST':
        # 标记商品为售出
        order.item.is_sold = True
        order.item.save()
        
        # 更新卖家销售统计
        try:
            seller_profile = order.seller.userprofile
            seller_profile.items_sold += 1
            seller_profile.save()
        except:
            pass  # 如果UserProfile不存在，跳过
        # 🔥 新增：更新买家购买统计
        try:
            buyer_profile = order.buyer.userprofile
            buyer_profile.items_bought += 1
            buyer_profile.save()
        except:
            pass  # 如果UserProfile不存在，跳过
        
        # 更新订单状态
        order.status = 'completed'
        order.save()
        
        messages.success(request, f'Order accepted! "{order.item.title}" has been marked as sold.')
        return redirect('my_items')
# Create your views here.