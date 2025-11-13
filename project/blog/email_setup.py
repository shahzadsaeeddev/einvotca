import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from rest_framework import status
from rest_framework.response import Response

#
def send_email(instance, subject, body):
    try:
        print(instance, subject, body)
        gmail_user = instance.email
        gmail_password = instance.password
        to = instance.notification_email
        template = body
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"no-reply  {gmail_user}"
        message["To"] = to
        part2 = MIMEText(template, "html")
        message.attach(part2)
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(instance.outgoing_server, instance.outgoing_port, context=context)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to, message.as_string())
        server.close()
        return Response({"status": "success", "message": "Email Sent Successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"status": "failed","message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

