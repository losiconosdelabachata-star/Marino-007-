"""
Email Service
Sends promotional email blasts to customers about new blog posts
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        """Initialize email service"""
        self.sender_email = os.getenv('EMAIL_SENDER', 'losiconosdelabachata@gmail.com')
        self.sender_password = os.getenv('EMAIL_PASSWORD', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))

    def send_blast_email(self, recipient_emails, subject, blog_title, blog_content, blog_url, products):
        """Send promotional email blast about a new blog post"""
        try:
            # Create HTML email template
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <!-- Header -->
                    <div style="background-color: #d4af37; padding: 20px; text-align: center; border-radius: 5px;">
                        <h1 style="color: white; margin: 0;">Los Iconos de la Bachata</h1>
                        <p style="color: white; margin: 5px 0;">Timeless Music, Timeless Stories</p>
                    </div>

                    <!-- Blog Section -->
                    <div style="margin: 30px 0; padding: 20px; background-color: #f9f9f9; border-left: 4px solid #d4af37;">
                        <h2 style="color: #d4af37; margin-top: 0;">📖 New Blog Post!</h2>
                        <h3 style="color: #333;">{blog_title}</h3>
                        <p style="color: #666;">{blog_content[:200]}...</p>
                        <a href="{blog_url}" style="display: inline-block; background-color: #d4af37; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Read Full Story →
                        </a>
                    </div>

                    <!-- Featured Products -->
                    <div style="margin: 30px 0;">
                        <h3 style="color: #d4af37;">🎵 Featured Products</h3>
                        <div style="display: flex; gap: 15px; flex-wrap: wrap;">
            """

            for product in products:
                html_content += f"""
                            <div style="flex: 1; min-width: 150px; text-align: center; padding: 15px; background-color: #f9f9f9; border-radius: 5px;">
                                <h4 style="margin: 0 0 10px 0;">{product['name']}</h4>
                                <p style="color: #d4af37; font-size: 18px; font-weight: bold; margin: 5px 0;">${product['price']}</p>
                                <a href="{product['url']}" style="color: #d4af37; text-decoration: none; font-weight: bold;">Shop Now →</a>
                            </div>
                """

            html_content += """
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #999; font-size: 12px;">
                        <p>© 2026 Los Iconos de la Bachata. All rights reserved.</p>
                        <p><a href="#" style="color: #d4af37; text-decoration: none;">Unsubscribe</a> |
                           <a href="#" style="color: #d4af37; text-decoration: none;">Preferences</a></p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email

            # Attach HTML
            message.attach(MIMEText(html_content, 'html'))

            # Send to each recipient
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)

                for recipient in recipient_emails:
                    message['To'] = recipient
                    server.send_message(message)
                    print(f"✅ Email sent to {recipient}")

            return True

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def load_customer_emails(self, file_path='customer_emails.txt'):
        """Load customer email list from file"""
        try:
            with open(file_path, 'r') as f:
                emails = [line.strip() for line in f if line.strip() and '@' in line]
            return emails
        except FileNotFoundError:
            print(f"⚠️  Customer email file not found: {file_path}")
            return []

    def add_customer_email(self, email, file_path='customer_emails.txt'):
        """Add a customer email to the list"""
        try:
            with open(file_path, 'a') as f:
                f.write(f"{email}\n")
            print(f"✅ Email added: {email}")
            return True
        except Exception as e:
            print(f"❌ Error adding email: {e}")
            return False

if __name__ == "__main__":
    # Test email service
    service = EmailService()

    # Example customer emails
    test_emails = ['customer@example.com']

    # Example blog data
    blog_data = {
        'title': 'The History of Los Iconos de la Bachata',
        'content': 'Los Iconos de la Bachata has been creating timeless music for decades...',
        'url': 'https://losiconosdelabachata.com/blog/history',
        'products': [
            {'name': 'Vinyl Album', 'price': '29.99', 'url': 'https://shop.losiconosdelabachata.com/vinyl'},
            {'name': 'CD Collection', 'price': '19.99', 'url': 'https://shop.losiconosdelabachata.com/cd'},
        ]
    }

    # Send test email
    service.send_blast_email(
        test_emails,
        'New Blog: The History of Los Iconos de la Bachata',
        blog_data['title'],
        blog_data['content'],
        blog_data['url'],
        blog_data['products']
    )
