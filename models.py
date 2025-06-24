from django.db import models
from datetime import date
# Create your models here.
class EmployeeForm(models.Model):
    
    Employee_Name = models.CharField(max_length=64)
    Employee_Id = models.CharField(max_length=64)
    Employee_LeaveReason = models.CharField(max_length=64)
   # Leave_Startdate = models.DateField()
   # Leave_Enddate = models.DateField()
    
    # string representation
    def __str__(self):
        return (f" EMPLOYEE NAME:{self.Employee_Name}, EMPLYOEE ID: {self.Employee_Id}, LEAVE REASON: {self.Employee_LeaveReason}")
