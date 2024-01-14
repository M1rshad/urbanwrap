from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from .forms import SignupForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from home.views import index
# Create your views here.
def sign_up(request):
    form = SignupForm()
    if request.POST:
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(log_in)
    context = {'form' : form}
    return render(request, 'user_auth/user_signup.html', context)

def log_in(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(email=email, password=password)
    if user is not None and user.is_active:
        login(request, user)
        url = 'home/index.html'
        return redirect(index)
    else:
        messages.error(request, 'Invalid username or password')
    return render(request, 'user_auth/user_login.html')

def log_out(request):
    logout(request)
    return redirect(index)