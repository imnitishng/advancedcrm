import os

from django.shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from PIL import Image

from .models import User
from .forms import UserListForm, UserListModelForm
from .utils import send_mass_html_mail

# Create your views here.
def index(request):
    users = get_list_or_404(User, email_address__isnull=False)
    return render(request, 'marketingemails/index.html', {'users': users})

def sendmail(request):

    def build_email(name, email_address):
        text_content = f"""
            Hi {name}, 
                Here are some properties you might be interested in,
                link.
            """
        context = {
            'name': name
        }

        html_content = render_to_string('mails/campaign1.html', {'context': context})        
        subject = "Recommendations"
        
        return subject, text_content, html_content

    users_to_mail_data = []
    user_pkids = request.POST.getlist('user_selected')
    for user_id in user_pkids:
        user = get_object_or_404(User, pk=user_id)
        subject, text_mail, html_mail = build_email(user.name, user.email_address)
        users_to_mail_data.append((subject, text_mail, html_mail, 'imnitish.ng@gmail.com', user.email_address))
    
    send_mass_html_mail(users_to_mail_data)

    return render(request, 'marketingemails/testmailsent.html')

def image_load(request):
    print("\nImage Loaded\n")
    red = Image.new('RGB', (1, 1))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    return response