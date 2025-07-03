# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Employee, LeaveApplication
from .forms import LeaveApplicationForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'leaves/login.html')

@login_required
def dashboard(request):
    try:
        employee = Employee.objects.get(user=request.user)
        leave_applications = LeaveApplication.objects.filter(employee=employee).order_by('-applied_on')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact administrator.')
        return redirect('login')
    
    context = {
        'employee': employee,
        'leave_applications': leave_applications,
    }
    return render(request, 'leaves/dashboard.html', context)

@login_required
def apply_leave(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact administrator.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave_application = form.save(commit=False)
            leave_application.employee = employee
            leave_application.save()
            messages.success(request, 'Leave application submitted successfully!')
            return redirect('dashboard')
    else:
        form = LeaveApplicationForm()
    
    return render(request, 'leaves/apply_leave.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')