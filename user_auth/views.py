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
            messages.success(request, 'Your account is created')
            return redirect(log_in)
    context = {'form' : form}
    return render(request, 'user_auth/user_signup.html', context)

def log_in(request):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            if hasattr(user, 'is_block') and user.is_block:  # Check if the user is blocked
                messages.error(request, 'Your account is blocked. Please contact support.')
            elif not user.is_block:  # Check if the user is not blocked
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
        

    return render(request, 'user_auth/user_login.html')

def log_out(request):
    logout(request)
    return redirect(index)