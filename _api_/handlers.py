from django.utils.log import AdminEmailHandler
from django.core.mail import send_mail
import traceback

class CustomEmailHandler(AdminEmailHandler):
    def send_mail(self, subject, message, *args, **kwargs):
       
        full_message = f"{subject}\n\n{message}\n\n"
        
        if 'exc_info' in kwargs:
            exception_info = traceback.format_exception(*kwargs['exc_info'])
            full_message += f"Traceback:\n{''.join(exception_info)}"
        
        send_mail(
            subject=f"Custom Error: {subject}",
            message=full_message,
            from_email="info@swalook.in",
            recipient_list=["debashishsarkar90072@gmail.com","sarthak@swalook.in","sai@swalook.in","hrittik@swalook.in","bijit@swalook.in","promoth@swalook.in","debashish@swalook.in"],
            fail_silently=False,
        )
