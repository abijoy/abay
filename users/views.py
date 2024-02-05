from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_ratelimit.decorators import ratelimit

from django.http import (
    HttpResponse, HttpResponseRedirect
)

from django.contrib.auth import (
    get_user_model, 
    authenticate,
    login
)

from .forms import (
    CustomUserCreationForm,
    LoginForm
)

from .models import (
    Profile,
    AccountVerificationToken,
    EmailVerificationCode
)

from .utils import (
    generate_email_verification_code,
    send_email_verification_code
)


@ratelimit(key='header:x-real-ip', rate='10/h')
def myview(request):
    print(request.META)
    # limited to 10 req/minute for a given user or client IP
    return HttpResponse('Rate Limited view')


def login_view(request):
    # print(request.META)
    print(request.META['REMOTE_ADDR'])
    if request.method == 'POST':
        form = LoginForm(request.POST)
        next = request.POST.get('next', '/')
        print(next)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # user = get_user_model().objects.get(username=username, email)

            user = authenticate(request, username=username, password=password)
            print('------------USER----------', user)
            # print(request.user.email)

            if user:
                login(request, user, backend='users.backends.EmailBackend')
                return HttpResponseRedirect(next)
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    
    form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def home(request):

    from django.contrib.sites.shortcuts import get_current_site
    print(get_current_site(request))
    profile = request.user.profile if request.user.is_authenticated else None
    text = f'''
    <h3> User is {request.user} - Profile {profile} </h3>
    '''
    text += '''
    <button>Verify Your email</button> <a href='/accounts/login/'>Login</a> <br>
    <a href='/register/'>Register</a>
    ''' if not request.user.email_confirmation else ''

    return HttpResponse(text)



def generate_account_verification_token(user):
    from django.contrib.auth.tokens import default_token_generator
    token = default_token_generator.make_token(user)
    return token


def send_verification_link_via_email(request, token):
    from django.template.loader import render_to_string
    from django.core.mail import EmailMessage
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    verification_link = f'{request.scheme}://{request.get_host()}/accounts/verify/{token}/'

    mail_subject = 'Please Verify Your Account.'
    to_email = request.user.email

    msg = EmailMultiAlternatives(
        subject=mail_subject,
        body='Account Verification Email', 
        from_email=settings.EMAIL_HOST_USER,
        to=(to_email, )
    )

    html_content = render_to_string('users/account_verification_email.html', {
        'user': request.user,
        'verification_link': verification_link,
    })

    msg.attach_alternative(html_content, 'text/html')
    msg.send()

    # email = EmailMessage(
    #     mail_subject, message, to=(to_email, )
    # )
    # email.send()


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            try:
                new_user = form.save(commit=False)
                # add anything you need to modify before saving the user
                # new_user.is_active = False
                new_user.save()

                # create a corresponding profile for the user
                p = Profile.objects.create(
                    user=new_user
                )
                p.save()
            except Exception as e:
                print(e)


            # now authenticate the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            authenticate(username=username, password=password) 
            # login(request, user)
            login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')

            # create account verification token and send the link via email
            try:


                # Email verification code
                try:
                    from django.utils import timezone
                    code = generate_email_verification_code()
                    code_obj = EmailVerificationCode.objects.create(
                        user=new_user,
                        code=code,
                    )
                    code_obj.save()
                    print(code_obj)
                    send_email_verification_code(request, code_obj.code)
                except Exception as e:
                    print(e)

                # send signup confirmation email
                # send_verification_link_via_email(request, token_obj.token)
                return redirect('verify-email')
            except Exception as e:
                print(e)
            return redirect('app:dashboard')
        return render(request, 'users/registration.html', {'form': form})

    form = CustomUserCreationForm()
    return render(request, 'users/registration.html', {'form': form})


def token_expired(token_obj):
    from datetime import datetime
    from django.utils import timezone

    time_diff = timezone.make_aware(datetime.now()) - token_obj.generated_at
    hours_went = time_diff.total_seconds() / 3600
    return hours_went >= 24


# from django.contrib.auth.decorators import login_required
# @login_required

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from django.contrib.auth import logout
def verify_account(request, token=None):
    # logout(request)
    print(get_client_ip(request))
    print(request.META['REMOTE_ADDR'])
    print('#############user########', request.user)
    return render(request, 'users/account_verification.html')
    token_obj = AccountVerificationToken.objects.filter(token=token).last()
    if not token_obj:
        print('Invalid token!')
        return redirect('app:dashboard')
    if token_expired(token_obj):
        messages.error(request, 'Account Verification Token is expired!')
        return redirect('login')

    else:
        user = token_obj.user
        if user.email_confirmation == True:
            authenticate(user)
            login(request, user, backend='users.backends.EmailBackend')
            messages.success(request, f'{request.user} is already verified!')
            return redirect('app:dashboard')
        else:
            user.email_confirmation = True
            user.is_active = True
            user.save()
            authenticate(user)
            login(request, user, backend='users.backends.EmailBackend')

            # add flush message here for account verfication
            messages.success(request, f'{request.user} is successfully verified!')

            #TODO: send onboard welcome email


            return redirect('app:dashboard')
    return redirect('app:dashboard')


def get_email_verification_code(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        user = request.user
        if user.is_authenticated:
            # invalid the last code requested by this user
            code_obj = EmailVerificationCode.objects.filter(user=user).last()
            code_obj.used = True
            code_obj.save()

            # now create a new code for this user
            try:
                from django.utils import timezone
                code = generate_email_verification_code()
                code_obj = EmailVerificationCode.objects.create(
                    user=user,
                    code=code,
                )
                code_obj.save()
                print(code_obj)
                send_email_verification_code(request, code_obj.code)
                return JsonResponse({'message': 'SUCCESS'}, status=200)
            except Exception as e:
                print(e)
                return JsonResponse({'message': 'FAILED'}, status=500)
            
    return JsonResponse({'error': 'Unauthorized'}, status=401)


from django.http import JsonResponse
import json
@login_required
def verify_email_verification_code(request):
    if request.user.email_confirmation == True:
        messages.success(request, f'{request.user} is already verified!')
        return redirect('/')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        code = json.loads(request.body)
        print('--------CODE----------: ', code)

        # pythonanywhere fix: getting the email verification code
        # Bypass the verification system using this code 
        # if you are not be able to get verification code in email
        if code == '112233':
            data = {
                'message': 'SUCCESS',
                'success_url': f'/'
            }
            return JsonResponse(data)

        user = request.user
        code_obj = EmailVerificationCode.objects.filter(user=user, code=code).last()
        if code_obj:
            if not code_obj.expired and not code_obj.used:
                user.email_confirmation = True
                user.save()
                code_obj.used = True
                code_obj.save()
                data = {
                    'message': 'SUCCESS',
                    'success_url': f'/'
                }
            else:
                data = {
                    'message': 'Code Expired',
                    'success_url': f'/'
                }
        else:
            data = {
                'message': 'Not a valid Code',
                'success_url': f'/'
            }
        return JsonResponse(data)
    
    return render(request, 'users/account_verification.html')
