# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

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
    
    def __str__(self):
        return f"{self.employee.user.username} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.send_notification_email()
    
    def send_notification_email(self):
        subject = f'Leave Application - {self.employee.user.get_full_name()}'
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

        Please review and take appropriate action.

        Best regards,
        Leave Management System
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [self.employee.manager_email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")