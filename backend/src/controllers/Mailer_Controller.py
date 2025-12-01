import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

class Mailer_Controller():
    def __init__(self, host, port, user, pwd, sender, receiver):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.sender = sender
        self.receiver = receiver

    def send_emergency_alert(self):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg['Subject'] = "🚨 SENTRIX Intrusion Alert"

        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color:#d9534f;">🚨 Sentrix Security Emergency Alert</h2>

                <p><strong>Alert:</strong> Intrusion Detected</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Location:</strong> Home Security System</p>

                <p style="margin-top:20px; font-size: 15px;">
                    Your Sentrix security system has detected an intrusion. Immediate attention is recommended.
                </p>

                <hr>
                <p style="color:#888; font-size: 12px;">
                    This is an automated message from your Sentrix Alarm IoT system.
                </p>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls(context=context)
            server.login(self.user, self.pwd)
            server.sendmail(self.sender, self.receiver, msg.as_string())