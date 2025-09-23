from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/add/', views.add_item, name='add_item'),
    path('item/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('image/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('change-password/', views.change_password, name='change_password'),
]