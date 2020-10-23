from django.core.mail import get_connection, EmailMultiAlternatives


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    connection = connection or get_connection(username=user, password=password, 
    fail_silently=fail_silently)

    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, [recipient])
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

def dictionary_to_str(dic):
    pass