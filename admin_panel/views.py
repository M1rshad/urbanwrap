from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from user_auth.models import User
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.postgres.search import SearchVector
# Create your views here.
@never_cache
def admin_login(request):
    if request.user.is_authenticated:
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
def admin_panel(request):
    return render(request, 'admin_panel/admin_panel.html')


def log_out(request):
    logout(request)
    return redirect(admin_login)

@never_cache
def user_management(request):
    user_obj = User.objects.all()
    context = {'user_obj' : user_obj}
    return render(request, 'admin_panel/user_management.html',context)


def delete_user(request,pk):
    instance = User.objects.get(pk=pk)
    instance.delete()
    user_obj = User.objects.all()
    context = {'user_obj' : user_obj}
    return render(request, 'admin_panel/user_management.html',context)


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
