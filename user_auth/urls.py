from django.urls import path
from . import views
urlpatterns = [
    path('user/signup/',views.sign_up, name='sign_up'),
    path('user/login/',views.log_in, name='log_in'),
    path('user/logout/',views.log_out, name='log_out'),
    path('user/otp/',views.otp_view, name='otp_signup'),
    path('user/resend-otp/',views.resend_otp, name='resend_otp'),
    path('user/forgot-password/',views.forgot_password, name='forgot_password'),
    path('user/forgot-password-otp/',views.forgot_password_otp, name='forgot_password_otp'),
    path('user/resend-otp-2/',views.resend_otp_2, name='resend_otp_2'),
    path('user/change-password/',views.update_password, name='update_password'),




]