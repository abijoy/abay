def generate_email_verification_code():
    import random
    import time

    # Generate a 6 digit code based on unix time.
    random.seed(time.time())
    code = random.randint(100000, 999999)
    return code

def send_email_verification_code(request, code):
    from django.template.loader import render_to_string
    from django.core.mail import EmailMessage
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    # verification_link = f'{request.scheme}://{request.get_host()}/accounts/verify/{token}/'

    mail_subject = 'Please Verify Your Email.'
    to_email = request.user.email

    msg = EmailMultiAlternatives(
        subject=mail_subject,
        body='Account Verification Email', 
        from_email=settings.EMAIL_HOST_USER,
        to=(to_email, )
    )

    html_content = render_to_string('users/email_verification_code.html', {
        'user': request.user,
        'verification_code': code,
    })

    msg.attach_alternative(html_content, 'text/html')
    msg.send()
