from django.urls import path
from . import views
urlpatterns = [
    path('user/signup/',views.sign_up, name='sign_up'),
    path('user/login/',views.log_in, name='log_in'),
    path('user/logout/',views.log_out, name='log_out'),
    path('user/otp/',views.otp_view, name='otp_signup'),
    path('user/resend-otp/',views.resend_otp, name='resend_otp'),

]