from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Employee, LeaveApplication
from .serializers import EmployeeSerializer, LeaveApplicationSerializer, LeaveApplicationCreateSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Employees can only see their own data unless they're staff
        if self.request.user.is_staff:
            return Employee.objects.all()
        return Employee.objects.filter(user=self.request.user)

class LeaveApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Employees can only see their own leave applications unless they're staff
        if self.request.user.is_staff:
            return LeaveApplication.objects.all()
        try:
            employee = Employee.objects.get(user=self.request.user)
            return LeaveApplication.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            return LeaveApplication.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveApplicationCreateSerializer
        return LeaveApplicationSerializer
    
    def perform_create(self, serializer):
        try:
            employee = Employee.objects.get(user=self.request.user)
            serializer.save(employee=employee)
        except Employee.DoesNotExist:
            raise ValidationError("Employee profile not found.")

@api_view(['GET'])
@permission_classes([AllowAny])
def approve_leave(request, token):
    """Approve leave application via email link"""
    leave_application = get_object_or_404(LeaveApplication, approval_token=token)
    
    if leave_application.status != 'pending':
        return render(request, 'leaves/action_result.html', {
            'title': 'Already Processed',
            'message': f'This leave request has already been {leave_application.status}.',
            'status': 'warning'
        })
    
    # Update status
    leave_application.status = 'approved'
    leave_application.save()
    
    # Send confirmation email to employee
    send_confirmation_email(leave_application, 'approved')
    
    return render(request, 'leaves/action_result.html', {
        'title': 'Leave Approved',
        'message': f'Leave request for {leave_application.employee.user.get_full_name()} has been approved successfully.',
        'employee': leave_application.employee.user.get_full_name(),
        'leave_type': leave_application.get_leave_type_display(),
        'start_date': leave_application.start_date,
        'end_date': leave_application.end_date,
        'status': 'approved'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def reject_leave(request, token):
    """Reject leave application via email link"""
    leave_application = get_object_or_404(LeaveApplication, approval_token=token)
    
    if leave_application.status != 'pending':
        return render(request, 'leaves/action_result.html', {
            'title': 'Already Processed',
            'message': f'This leave request has already been {leave_application.status}.',
            'status': 'warning'
        })
    
    # Update status
    leave_application.status = 'rejected'
    leave_application.save()
    
    # Send confirmation email to employee
    send_confirmation_email(leave_application, 'rejected')
    
    return render(request, 'leaves/action_result.html', {
        'title': 'Leave Rejected',
        'message': f'Leave request for {leave_application.employee.user.get_full_name()} has been rejected.',
        'employee': leave_application.employee.user.get_full_name(),
        'leave_type': leave_application.get_leave_type_display(),
        'start_date': leave_application.start_date,
        'end_date': leave_application.end_date,
        'status': 'rejected'
    })

def send_confirmation_email(leave_application, action):
    """Send confirmation email to employee about leave status"""
    subject = f'Leave Request {action.title()} - {leave_application.get_leave_type_display()}'
    
    message = f"""
    Dear {leave_application.employee.user.get_full_name()},

    Your leave request has been {action}.

    Leave Details:
    - Leave Type: {leave_application.get_leave_type_display()}
    - Start Date: {leave_application.start_date}
    - End Date: {leave_application.end_date}
    - Status: {action.title()}
    - Comments: {leave_application.comments or 'No comments provided'}

    Best regards,
    Leave Management System
    """
    
    html_message = f"""
    <html>
    <body>
        <h2>Leave Request {action.title()}</h2>
        <p>Dear {leave_application.employee.user.get_full_name()},</p>
        
        <p>Your leave request has been <strong>{action}</strong>.</p>
        
        <h3>Leave Details:</h3>
        <ul>
            <li><strong>Leave Type:</strong> {leave_application.get_leave_type_display()}</li>
            <li><strong>Start Date:</strong> {leave_application.start_date}</li>
            <li><strong>End Date:</strong> {leave_application.end_date}</li>
            <li><strong>Status:</strong> <span style="color: {'green' if action == 'approved' else 'red'};">{action.title()}</span></li>
            <li><strong>Comments:</strong> {leave_application.comments or 'No comments provided'}</li>
        </ul>
        
        <p>Best regards,<br>Leave Management System</p>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [leave_application.employee.user.email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")