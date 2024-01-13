from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from user_auth.models import User
from home.models import Category, Product
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.postgres.search import SearchVector
from user_auth.forms import SignupForm
from .forms import EditUserForm, AddCategoryForm, AddProductForm
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
def delete_user(request,pk):
    instance = User.objects.get(pk=pk)
    instance.delete()
    return redirect('user_management')


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
def edit_user(request, pk):
    instance = User.objects.get(pk=pk)
    if request.POST:
        form = EditUserForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(user_management)
    form = EditUserForm(instance=instance)
    context = {'form': form}
    return render(request, 'admin_panel/edit_user.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def add_user(request):
    form = SignupForm()
    if request.POST:
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(user_management)
    context = {'form' : form}
    return render(request, 'admin_panel/add_user.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def block_user(request,pk):
    instance = User.objects.get(pk=pk)
    instance.is_active = False
    instance.save()
    return redirect('user_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def unblock_user(request,pk):
    instance = User.objects.get(pk=pk)
    instance.is_active = True
    instance.save()
    return redirect('user_management')


@never_cache
@user_passes_test(is_user_admin, login_url='admin_login')
def category_management(request):
    cat_obj = Category.objects.all().order_by('id')
    context = {'cat_obj' : cat_obj}
    return render(request, 'admin_panel/category_management.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def delete_category(request, pk):
    instance = Category.objects.get(pk=pk)
    instance.delete()
    return redirect('category_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def add_category(request):
    form = AddCategoryForm()
    if request.POST:
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(category_management)
    context = {'form' : form}
    return render(request, 'admin_panel/add_category.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def edit_category(request, pk):
    instance = Category.objects.get(pk=pk)
    if request.POST:
        form = AddCategoryForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(category_management)
    form = AddCategoryForm(instance=instance)
    context = {'form': form}
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
def delete_product(request, pk):
    instance = Product.objects.get(pk=pk)
    instance.delete()
    return redirect('product_management')


@user_passes_test(is_user_admin, login_url='admin_login')
def add_product(request):
    form = AddProductForm()
    if request.POST:
        form = AddProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(product_management)
    context = {'form' : form}
    return render(request, 'admin_panel/add_product.html',context)


@user_passes_test(is_user_admin, login_url='admin_login')
def edit_product(request, pk):
    instance = Product.objects.get(pk=pk)
    if request.POST:
        form = AddProductForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(product_management)
    form = AddProductForm(instance=instance)
    context = {'form': form}
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