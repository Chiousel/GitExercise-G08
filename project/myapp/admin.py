from django.contrib import admin
from .models import Item, ItemImage, PickupPoint

admin.site.register(Item)
admin.site.register(ItemImage)
admin.site.register(PickupPoint)

# Register your models here.
