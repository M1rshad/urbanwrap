from datetime import datetime,timedelta
import pyotp
from django.core.mail import send_mail

def send_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = totp.now()
    request.session['otp_secret_key']= totp.secret
    valid_date = datetime.now() + timedelta(minutes = 1)
    request.session['otp_valid_date'] = str(valid_date)
    print(otp)
    send_mail("UrbanWrap - OTP for Sign up", otp, "abdullamirshadcl@gmail.com", [request.session['email']], fail_silently=False)

