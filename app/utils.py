import smtplib
from email.mime.text import MIMEText

def send_verify_email(to_email, code):
    subject = "Xác nhận đăng ký tài khoản"
    body = f"Mã xác nhận của bạn là: {code}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'nguyenchinhnhan04@gmail.com'
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('nguyenchinhnhan04@gmail.com', 'xsxu bhmw zasn fctc')
            smtp.send_message(msg)
            print(f"✅ Đã gửi mã xác nhận đến {to_email}")
    except Exception as e:
        print("❌ Gửi email thất bại:", e)
