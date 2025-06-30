# Register your models here.
from django.contrib import admin
from .models import Employee, LeaveApplication

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'manager_email']
    search_fields = ['user__username', 'employee_id', 'user__first_name', 'user__last_name']

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on']
    list_filter = ['leave_type', 'status', 'applied_on']
    search_fields = ['employee__user__username', 'employee__employee_id']
    date_hierarchy = 'applied_on'