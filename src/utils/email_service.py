import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', 'your-email@gmail.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'your-app-password')
        self.company_email = os.getenv('COMPANY_EMAIL', 'bookings@zoomgorides.com')
        
    def send_booking_confirmation(self, booking):
        """Send booking confirmation email to customer"""
        try:
            subject = f"Booking Confirmation - {booking.booking_id}"
            
            # Create HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #003366; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .booking-details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                    .footer {{ background-color: #003366; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                    .status {{ background-color: #ffc107; color: #856404; padding: 5px 10px; border-radius: 3px; display: inline-block; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Zoom & Go Rides</h1>
                        <h2>Booking Confirmation</h2>
                    </div>
                    
                    <div class="content">
                        <p>Dear {booking.first_name} {booking.last_name},</p>
                        
                        <p>Thank you for choosing Zoom & Go Rides! Your booking has been received and is currently being processed.</p>
                        
                        <div class="booking-details">
                            <h3>Booking Details</h3>
                            <p><strong>Booking ID:</strong> {booking.booking_id}</p>
                            <p><strong>Status:</strong> <span class="status">{booking.status.upper()}</span></p>
                            <p><strong>Service:</strong> {booking.service_type.replace('_', ' ').title()}</p>
                            <p><strong>Vehicle:</strong> {booking.vehicle_type.replace('_', ' ').title()}</p>
                            <p><strong>Date & Time:</strong> {booking.pickup_date} at {booking.pickup_time}</p>
                            <p><strong>Pickup Location:</strong> {booking.pickup_location}</p>
                            <p><strong>Drop-off Location:</strong> {booking.dropoff_location}</p>
                            <p><strong>Passengers:</strong> {booking.passengers}</p>
                            {f'<p><strong>Estimated Price:</strong> ${booking.estimated_price:.2f}</p>' if booking.estimated_price else ''}
                            {f'<p><strong>Special Requests:</strong> {booking.special_requests}</p>' if booking.special_requests else ''}
                        </div>
                        
                        <p><strong>What's Next?</strong></p>
                        <ul>
                            <li>Our team will review your booking within 2 hours</li>
                            <li>You will receive a confirmation call or email with final details</li>
                            <li>A driver will be assigned and you'll receive their contact information</li>
                        </ul>
                        
                        <p>If you have any questions or need to make changes, please contact us:</p>
                        <p>📞 Phone: +1 (555) 123-4567<br>
                        📧 Email: bookings@zoomgorides.com</p>
                    </div>
                    
                    <div class="footer">
                        <p>&copy; 2025 Zoom & Go Rides. All rights reserved.</p>
                        <p>123 Transportation Ave, Dallas, TX 75201</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(booking.email, subject, html_content)
            
        except Exception as e:
            print(f"Error sending booking confirmation: {str(e)}")
            return False
    
    def send_admin_notification(self, booking):
        """Send new booking notification to admin"""
        try:
            subject = f"New Booking Received - {booking.booking_id}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .booking-details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                    .urgent {{ background-color: #ff6b6b; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 New Booking Alert</h1>
                    </div>
                    
                    <div class="content">
                        <div class="urgent">
                            <strong>Action Required:</strong> New booking needs review and confirmation
                        </div>
                        
                        <div class="booking-details">
                            <h3>Booking Information</h3>
                            <p><strong>Booking ID:</strong> {booking.booking_id}</p>
                            <p><strong>Customer:</strong> {booking.first_name} {booking.last_name}</p>
                            <p><strong>Email:</strong> {booking.email}</p>
                            <p><strong>Phone:</strong> {booking.phone}</p>
                            <p><strong>Service:</strong> {booking.service_type.replace('_', ' ').title()}</p>
                            <p><strong>Vehicle:</strong> {booking.vehicle_type.replace('_', ' ').title()}</p>
                            <p><strong>Date & Time:</strong> {booking.pickup_date} at {booking.pickup_time}</p>
                            <p><strong>Pickup:</strong> {booking.pickup_location}</p>
                            <p><strong>Drop-off:</strong> {booking.dropoff_location}</p>
                            <p><strong>Passengers:</strong> {booking.passengers}</p>
                            <p><strong>Estimated Price:</strong> ${booking.estimated_price:.2f}</p>
                            <p><strong>Submitted:</strong> {booking.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                            {f'<p><strong>Special Requests:</strong> {booking.special_requests}</p>' if booking.special_requests else ''}
                        </div>
                        
                        <p><strong>Next Steps:</strong></p>
                        <ul>
                            <li>Review booking details</li>
                            <li>Confirm availability</li>
                            <li>Assign driver</li>
                            <li>Contact customer for confirmation</li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return self._send_email(self.company_email, subject, html_content)
            
        except Exception as e:
            print(f"Error sending admin notification: {str(e)}")
            return False
    
    def _send_email(self, to_email, subject, html_content):
        """Send email using SMTP"""
        try:
            # For demo purposes, we'll just print the email content
            # In production, you would configure actual SMTP settings
            print(f"📧 EMAIL SENT TO: {to_email}")
            print(f"📧 SUBJECT: {subject}")
            print(f"📧 CONTENT: {html_content[:200]}...")
            return True
            
           msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = self.email_user
msg['To'] = to_email

html_part = MIMEText(html_content, 'html')
msg.attach(html_part)

server = smtplib.SMTP(self.smtp_server, self.smtp_port)
server.starttls()
server.login(self.email_user, self.email_password)
server.send_message(msg)
server.quit()

return True

            
        except Exception as e:
            print(f"Error in _send_email: {str(e)}")
            return False

