from django.shortcuts import render
from .models import EmployeeForm

# Create your views here.
from django.http import HttpResponse

def index(request):
    Employee = EmployeeForm.objects.all()
    context = {'Employee':Employee}  
    #return HttpResponse("Employee Form")
    return render(request, 'Employee/index.html', context)