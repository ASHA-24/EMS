from django.shortcuts import render,redirect
from django.core.mail import send_mail
# Create your views here.
from django.contrib import messages
from .forms import LeaveRequestForm
from .models import LeaveRequest

def leave_request_view(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('leave_request')
        else:
            messages.error(request, 'Please correct the errors below.')
            
        #send email
        employeename = {LeaveRequest.employee_name}
        leave_type = {LeaveRequest.leave_type}
        start_date = {LeaveRequest.start_date}
        end_date = {LeaveRequest.end_date}
        comments = {LeaveRequest.comments}
        send_mail(
            employeename + 'has submitted leave request',
            employeename + 'has submitted leaves starting from' + start_date + 'to' + end_date ,
            'asha1008sumi@gmail.com',
            'asha1008sumi@gmail.com'       
        )
    else:
        form = LeaveRequestForm()
    
    return render(request, 'leaves/leave_request.html', {'form': form})

def leave_list_view(request):
    """Optional view to display all leave requests"""
    leaves = LeaveRequest.objects.all()
    return render(request, 'leaves/leave_list.html', {'leaves': leaves})