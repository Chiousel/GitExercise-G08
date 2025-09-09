from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Item, ItemImage
from .forms import ItemForm, ItemImageForm

def item_list(request):
    query = request.GET.get('q')
    items = Item.objects.filter(is_sold=False).order_by('-created_at')
    if query:
        items = items.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(request, 'market/item_list.html', {'items': items})


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'market/item_detail.html', {'item': item})


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

# Create your views here.
