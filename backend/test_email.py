import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("smtplib imported successfully!")  # This should print without errors

# Optional: Quick send test (replace with your details; requires env vars)
email_user = "anshu290290@gmail.com"  # Set as os.getenv("EMAIL_USER")
email_pass = "jktl oqph ubci gppe"     # Set as os.getenv("EMAIL_PASS") – use app password for Gmail
to_email = "anshucrp87@gmail.com"
msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = to_email
msg['Subject'] = "Test"
msg.attach(MIMEText("Hello from Emily!", 'plain'))

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_pass)
    server.sendmail(email_user, to_email, msg.as_string())
    server.quit()
    print("Test email sent!")
except Exception as e:
    print(f"Send failed: {e} (check credentials/env vars)")