from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from user_auth.models import User
from home.models import Category, Product, Variation , ProductImages
from orders.models import Coupon
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.postgres.search import SearchVector
from user_auth.forms import SignupForm
from .forms import EditUserForm, AddCategoryForm, AddProductForm, AddVariantForm, ProductImageForm, AddCouponForm
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.
def is_user_admin(user):
    return user.is_authenticated and user.is_superuser


@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect(admin_panel)
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect(admin_panel)
        else:
            messages.info(request, 'Please enter the correct email and password for a staff account.')
    return render(request, 'admin_panel/admin_login.html')


@never_cache
@user_passes_test(is_user_admin, login_url='admin_login')
def admin_panel(request):
    return render(request, 'admin_panel/admin_panel.html')


def log_out(request):
    logout(request)
    return redirect(admin_login)


@never_cache
@user_passes_test(is_user_admin, login_url='admin_login')
def user_management(request):
    user_obj = User.objects.all().order_by('id')
    context = {'user_obj' : user_obj}
    return render(request, 'admin_panel/user_management.html',context)



@user_passes_test(is_user_admin, login_url='admin_login')
def user_search(request):
    if request.POST:
        search_item = request.POST.get('search_input')
        if search_item == '':
            return redirect(user_management)
        user_obj = User.objects.annotate(
        search=SearchVector('username','email')).filter(search=search_item)
        context = {'user_obj':user_obj}
        return render(request, 'admin_panel/user_management.html',context)
    else:
        return redirect(user_management)


@user_passes_test(is_user_admin, login_url='admin_login')
def block_user(request,pk):
    instance = User.objects.get(pk=pk)
    instance.is_block = True
    instance.save()
    return redirect('user_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def unblock_user(request,pk):
    instance = User.objects.get(pk=pk)
    instance.is_block = False
    instance.save()
    return redirect('user_management')


@never_cache
@user_passes_test(is_user_admin, login_url='admin_login')
def category_management(request):
    cat_obj = Category.objects.all().order_by('id')
    context = {'cat_obj' : cat_obj}
    return render(request, 'admin_panel/category_management.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def unlist_category(request, pk):
    instance = Category.objects.get(pk=pk)
    instance.is_active = False
    instance.save()
    return redirect('category_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def list_category(request, pk):
    instance = Category.objects.get(pk=pk)
    instance.is_active = True
    instance.save()
    return redirect('category_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def add_category(request):
    form = AddCategoryForm()
    if request.POST:
        form = AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(category_management)
    context = {'form' : form}
    return render(request, 'admin_panel/add_category.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def edit_category(request, pk):
    error_category_name = None
    error_slug = None
    error_description = None
    error_cat_image = None
    instance = Category.objects.get(pk=pk)
    if request.POST:
        form = AddCategoryForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(category_management)
        else:
            error_category_name = form['category_name'].errors
            error_slug = form['slug'].errors
            error_description = form['description'].errors
            error_cat_image = form['cat_image'].errors
    form = AddCategoryForm(instance=instance)
    context = {'form': form, 
               'error_category_name':error_category_name,
               'error_slug':error_slug,
               'error_description':error_description,
               'error_cat_image': error_cat_image,
               }
    return render(request, 'admin_panel/edit_category.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def category_search(request):
    if request.POST:
        search_item = request.POST.get('search_input')
        if search_item == '':
            return redirect(category_management)
        cat_obj = Category.objects.annotate(
        search=SearchVector('category_name','slug')).filter(search=search_item)
        context = {'cat_obj':cat_obj}
        return render(request, 'admin_panel/category_management.html',context)
    else:
        return redirect(category_management)


@never_cache
@user_passes_test(is_user_admin, login_url='admin_login')
def product_management(request):
    prod_obj = Product.objects.all().order_by('id')
    context = {'prod_obj' : prod_obj}
    return render(request, 'admin_panel/product_management.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def unlist_product(request, pk):
    instance = Product.objects.get(pk=pk)
    instance.is_active=False
    instance.save()
    return redirect('product_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def list_product(request, pk):
    instance = Product.objects.get(pk=pk)
    instance.is_active=True
    instance.save()
    return redirect('product_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def add_product(request):
    if request.POST:
        form = AddProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            product = form.save()
            for img in request.FILES.getlist('image'):
                image = ProductImages(image=img, product=product)
                image.save()

            return redirect(product_management)
        else:
            print(form.errors)
            print(image_form.errors)
    form = AddProductForm()
    image_form = ProductImageForm()
    context = {
        'form' : form,
        'image_form' : image_form
        }
    return render(request, 'admin_panel/add_product.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def edit_product(request, pk):
    instance = Product.objects.get(pk=pk)
    if request.POST:
        form = AddProductForm(request.POST, instance=instance)
        image_form = ProductImageForm(request.POST, request.FILES, instance=instance)
        print(form.errors)

        if form.is_valid() and image_form.is_valid():
            product = form.save()
            print(form.errors)

            #delete option for image
            for existing_image in product.product_img.all():
                checkbox_name = f'delete_image_{existing_image.id}'
                if checkbox_name in request.POST and request.POST.get(checkbox_name) == 'on':
                    existing_image.delete()
                    print(form.errors)

            for img in request.FILES.getlist('image'):
                image = ProductImages(image=img, product=product)
                image.save()
            print(form.errors)

            print(form.errors)
            return redirect(product_management)
    form = AddProductForm(instance=instance)
    image_form = ProductImageForm(instance=instance)
    existing_images = instance.product_img.all()
    context = {
        'form': form,
        'image_form': image_form,
        'existing_images':existing_images
        }
    return render(request, 'admin_panel/edit_product.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def product_search(request):
    if request.POST:
        search_item = request.POST.get('search_input')
        if search_item == '':
            return redirect(product_management)
        prod_obj = Product.objects.annotate(
        search=SearchVector('product_name','slug')).filter(search=search_item)
        context = {'prod_obj':prod_obj}
        return render(request, 'admin_panel/product_management.html',context)
    else:
        return redirect(product_management)
    

@never_cache
@user_passes_test(is_user_admin, login_url='admin_login')
def variant_management(request):
    var_obj = Variation.objects.all().order_by('id')
    context = {'var_obj' : var_obj}
    return render(request, 'admin_panel/variant_management.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def delete_variant(request, pk):
    instance = Variation.objects.get(pk=pk)
    instance.delete()
    return redirect('variant_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def add_variant(request):
    form = AddVariantForm()
    if request.POST:
        form = AddVariantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(variant_management)
    context = {'form' : form}
    return render(request, 'admin_panel/add_variant.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def edit_variant(request, pk):
    instance = Variation.objects.get(pk=pk)
    if request.POST:
        form = AddVariantForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            return redirect(variant_management)
    form = AddVariantForm(instance=instance)
    context = {'form': form}
    return render(request, 'admin_panel/edit_variant.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def variant_search(request):
    if request.POST:
        search_item = request.POST.get('search_input')
        if search_item == '':
            return redirect(variant_management)
        var_obj = Variation.objects.annotate(
        search=SearchVector('product','variation_category')).filter(search=search_item)
        context = {'var_obj':var_obj}
        return render(request, 'admin_panel/variant_management.html',context)
    else:
        return redirect(variant_management)
    

@user_passes_test(is_user_admin, login_url='admin_login')
def coupon_management(request):
    coupon_obj = Coupon.objects.all().order_by('id')
    context = {'coupon_obj' : coupon_obj}
    return render(request, 'admin_panel/coupon_management.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def add_coupon(request):
    form = AddCouponForm()
    if request.POST:
        form = AddCouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(coupon_management)
    context = {'form' : form}
    return render(request, 'admin_panel/add_coupon.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def unlist_coupon(request, pk):
    instance = Coupon.objects.get(pk=pk)
    instance.is_active=False
    instance.save()
    return redirect('coupon_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def list_coupon(request, pk):
    instance = Coupon.objects.get(pk=pk)
    instance.is_active=True
    instance.save()
    return redirect('coupon_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def edit_coupon(request, pk):
    instance = Coupon.objects.get(pk=pk)
    if request.POST:
        form = AddCouponForm(request.POST,instance=instance)
        if form.is_valid():
            form.save()
            return redirect(coupon_management)
    form = AddCouponForm(instance=instance)
    context = {'form': form}
    return render(request, 'admin_panel/edit_coupon.html',context)
