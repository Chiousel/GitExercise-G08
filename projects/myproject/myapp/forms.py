from django import forms
from .models import Item, ItemImage

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'price', 'condition', 'pickup_point']


class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']
