from django.db import models
from django.contrib.auth.models import User


class PickupPoint(models.Model):
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} (Floor: {self.floor})"



class Item(models.Model):
    CONDITION_CHOICES = [
        ("New", "New"),
        ("Used", "Used"),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-created_at']


# 📷 Multiple Images for Each Item
class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='item_images/')

    def __str__(self):
        return f"Image for {self.item.title}"

# 在market/models.py末尾添加
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_buyer')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_seller')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.item.title}"
    
    def save(self, *args, **kwargs):
        # 检查状态是否变为completed
        is_new = self._state.adding  # 判断是否是新建对象
        
        if not is_new:  # 如果是更新操作
            try:
                old_status = Order.objects.get(pk=self.pk).status
                if old_status != 'completed' and self.status == 'completed':
                    self.update_user_counts()
            except Order.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def update_user_counts(self):
        """更新买卖双方的计数"""
        try:
            # 更新卖家售出计数
            seller_profile = self.seller.userprofile
            seller_profile.items_sold += 1
            seller_profile.save()
            
            # 更新买家购买计数 ← 这就是缺失的功能！
            buyer_profile = self.buyer.userprofile  
            buyer_profile.items_bought += 1
            buyer_profile.save()
            
            # 标记物品为已售出
            self.item.is_sold = True
            self.item.save()
            
            print(f"✅ 订单 #{self.id} 完成：卖家 {self.seller.username} 售出数+1，买家 {self.buyer.username} 购买数+1")
            
        except UserProfile.DoesNotExist:
            # 如果UserProfile不存在，创建它
            from accounts.models import UserProfile
            UserProfile.objects.get_or_create(user=self.seller)
            UserProfile.objects.get_or_create(user=self.buyer)
            # 重试更新计数
            self.update_user_counts()
    
    class Meta:
        ordering = ['-created_at']
# Create your models here.