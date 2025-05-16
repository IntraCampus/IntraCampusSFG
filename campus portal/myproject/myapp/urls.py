from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 👈 Default homepage
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create_user/', views.create_user, name='create_user'),
    path('create_timetable/', views.create_timetable, name='create_timetable'),
    path('create_notification/', views.create_notification, name='create_notification'),
    path('profile/', views.user_profile, name='profile'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/dashboard/comment/<int:ann_id>/', views.post_announcement_comment, name='post_announcement_comment'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    
    path('notification/edit/<int:notif_id>/', views.edit_notification, name='edit_notification'),
    path('notification/delete/<int:notif_id>/', views.delete_notification, name='delete_notification'),
    path('maintenance/dashboard/', views.maintenance_dashboard, name='maintenance_dashboard'),
    path('admin/request-maintenance/', views.request_maintenance, name='request_maintenance'),
    path('send_alert/', views.send_alert_to_maintenance, name='send_alert_to_maintenance'),
    path('create_maintenance/', views.create_maintenance_request, name='create_maintenance_request'),
    path('maintenance/request/delete/<int:req_id>/', views.delete_maintenance_request, name='delete_maintenance_request'),
    path('edit_maintenance_request_modal/', views.edit_maintenance_request_modal, name='edit_maintenance_request_modal'),

    #Scheduling the classes 
    path('class-schedules/', views.view_class_schedules, name='view_class_schedules'),
    path('class-schedules/create/', views.create_class_schedule, name='create_class_schedule'),
    path('class-schedules/<int:schedule_id>/edit/', views.edit_class_schedule, name='edit_class_schedule'),
    path('class-schedules/<int:schedule_id>/delete/', views.delete_class_schedule, name='delete_class_schedule'),

    path('book-service/', views.book_service, name='book_service'),
    path('booked-services/', views.view_booked_services, name='view_booked_services'),

    path('system-overview/', views.system_overview, name='system_overview'),

]
 