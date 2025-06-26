from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_request_view, name='leave_request'),
    path('leave-list/', views.leave_list_view, name='leave_list'),
]
