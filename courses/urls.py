from django.urls import path
from . import views

app_name = 'courses'
urlpatterns = [
    path('', views.course_list, name='course-list'),
    path('master-data/', views.master_data_index, name='master-data-index'),
    path('master-data/<str:kind>/', views.master_data_list, name='master-data-list'),
    path('master-data/<str:kind>/add/', views.master_data_form, name='master-data-add'),
    path('master-data/<str:kind>/<int:pk>/edit/', views.master_data_form, name='master-data-edit'),
    path('master-data/<str:kind>/<int:pk>/delete/', views.master_data_delete, name='master-data-delete'),
    path('add/', views.course_add, name='course-add'),
    path('<int:pk>/edit/', views.course_edit, name='course-edit'),
    path('<int:pk>/delete/', views.course_delete, name='course-delete'),
    
    path('<int:course_pk>/sections/', views.section_list, name='section-list'),
    path('<int:course_pk>/add-section/', views.section_add, name='section-add'),
    path('section/<int:pk>/edit/', views.section_edit, name='section-edit'),
    path('section/<int:pk>/delete/', views.section_delete, name='section-delete'),
    path('section/<int:section_pk>/times/', views.time_list, name='time-list'),
    path('section/<int:section_pk>/times/add/', views.time_add, name='time-add'),
    path('times/<int:pk>/edit/', views.time_edit, name='time-edit'),
    path('times/<int:pk>/delete/', views.time_delete, name='time-delete'),
    
    path('register/', views.public_section_list, name='public-section-list'),
    path('enroll/<int:section_pk>/', views.enroll_section, name='enroll-section'),
    path('my-schedule/', views.my_schedule, name='my-schedule'),
    
    path('my_schedule/pdf/', views.my_schedule_pdf, name='my-schedule-pdf'),
]
