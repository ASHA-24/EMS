from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
from . import api_views
employeeviewset  = api_views.EmployeeViewSet
leavesviewset = api_views.LeaveApplicationViewSet
router.register(r'employees', employeeviewset, basename='employee')
router.register(r'leaves', leavesviewset, basename='leave')

urlpatterns = [
    path('', include(router.urls)),
    path('leave/<uuid:token>/approve/', api_views.approve_leave, name='approve_leave'),
    path('leave/<uuid:token>/reject/', api_views.reject_leave, name='reject_leave'),
    path('auth/', include('rest_framework.urls')),
]