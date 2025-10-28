from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.staff_login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='core:index'), name='logout'),
    
    path('students/', views.student_list, name='student-list'),
    path('students/<int:pk>/', views.student_detail, name='student-detail'),
]