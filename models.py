
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import uuid

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=10, unique=True)
    manager_email = models.EmailField()
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class LeaveApplication(models.Model):
    LEAVE_TYPES = [
        ('sick', 'Sick Leave'),
        ('casual', 'Casual Leave'),
        ('annual', 'Annual Leave'),
        ('emergency', 'Emergency Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    approval_token = models.UUIDField(default=uuid.uuid4, unique=True)
    
    def __str__(self):
        return f"{self.employee.user.username} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.send_notification_email()
    
    def send_notification_email(self):
        subject = f'Leave Application - {self.employee.user.get_full_name()}'
        
        # Generate approval and rejection URLs
        base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
        approve_url = f"{base_url}/api/leave/{self.approval_token}/approve/"
        reject_url = f"{base_url}/api/leave/{self.approval_token}/reject/"
        
        message = f"""
        Dear Manager,

        {self.employee.user.get_full_name()} (Employee ID: {self.employee.employee_id}) has applied for leave.

        Leave Details:
        - Employee: {self.employee.user.get_full_name()}
        - Leave Type: {self.get_leave_type_display()}
        - Start Date: {self.start_date}
        - End Date: {self.end_date}
        - Comments: {self.comments or 'No comments provided'}
        - Applied On: {self.applied_on.strftime('%Y-%m-%d %H:%M')}

        To take action on this leave request, please click on one of the links below:

        APPROVE: {approve_url}
        REJECT: {reject_url}

        Best regards,
        Leave Management System
        """
        
        html_message = f"""
        <html>
        <body>
            <h2>Leave Application Notification</h2>
            <p>Dear Manager,</p>
            
            <p><strong>{self.employee.user.get_full_name()}</strong> (Employee ID: {self.employee.employee_id}) has applied for leave.</p>
            
            <h3>Leave Details:</h3>
            <ul>
                <li><strong>Employee:</strong> {self.employee.user.get_full_name()}</li>
                <li><strong>Leave Type:</strong> {self.get_leave_type_display()}</li>
                <li><strong>Start Date:</strong> {self.start_date}</li>
                <li><strong>End Date:</strong> {self.end_date}</li>
                <li><strong>Comments:</strong> {self.comments or 'No comments provided'}</li>
                <li><strong>Applied On:</strong> {self.applied_on.strftime('%Y-%m-%d %H:%M')}</li>
            </ul>
            
            <h3>Action Required:</h3>
            <p>Please click on one of the buttons below to take action on this leave request:</p>
            
            <div style="margin: 20px 0;">
                <a href="{approve_url}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-right: 10px;">✓ APPROVE</a>
                <a href="{reject_url}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">✗ REJECT</a>
            </div>
            
            <p>Best regards,<br>Leave Management System</p>
        </body>
        </html>
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [self.employee.manager_email],
                fail_silently=False,
                html_message=html_message,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")