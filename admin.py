from django.contrib import admin

# Register your models here.
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee_name', 'employee_id', 'leave_type', 'start_date', 'end_date', 'created_at']
    list_filter = ['leave_type', 'start_date', 'created_at']
    search_fields = ['employee_name', 'employee_id']
    date_hierarchy = 'start_date'