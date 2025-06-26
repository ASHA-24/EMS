from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
        ('unpaid', 'Unpaid Leave'),
    ]
    
    employee_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee_name} - {self.leave_type}"
    
    class Meta:
        ordering = ['-created_at']