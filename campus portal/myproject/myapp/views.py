from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from .models import Notification, Timetable, MaintenanceRequest, Announcement, AnnouncementComment, ServiceBooking # FIXED imports
from django.db.models import Q  # Optional: for future filtering
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ClassSchedule
#from dashboard.models import Profile  # if profile is in dashboard app
from django.contrib.auth.models import User
from .forms import ClassScheduleForm ,ServiceBookingForm
from .models import Profile
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from .models import Test, TestSubmission
from .forms import TestForm, TestSubmissionForm
from django.contrib.auth.models import User

# Role check functions
def is_teacher(user):
    return hasattr(user, 'profile') and user.profile.role == 'teacher'

def is_student(user):
    return hasattr(user, 'profile') and user.profile.role == 'student'

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'


User = get_user_model()

# User Login
def user_login(request):
    if request.method == 'POST':
        username      = request.POST.get('username')
        password      = request.POST.get('password')
        selected_role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)
        if not user:
            messages.error(request, "Invalid username or password.")
            return render(request, 'myapp/login.html')

        try:
            actual_role = user.profile.role
        except Exception:
            actual_role = None

        if actual_role != selected_role:
            messages.error(request, f"Your account role is '{actual_role or 'unset'}', not '{selected_role}'.")
            return render(request, 'myapp/login.html')

        login(request, user)

        if selected_role == 'admin':
            return redirect('admin_dashboard')
        elif selected_role == 'teacher':
            return redirect('teacher_dashboard')
        elif selected_role == 'student':
            return redirect('student_dashboard')
        elif selected_role == 'maintenance':
            return redirect('maintenance_dashboard')
        else:
            return redirect('dashboard')

    return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    timetables    = Timetable.objects.order_by('-uploaded_at')
    notifications = Notification.objects.order_by('-created_at')
    return render(request, 'myapp/dashboard.html', {
        'timetables': timetables,
        'notifications': notifications,
    })


@login_required
def admin_dashboard(request):
    if request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('login')

    users = User.objects.exclude(is_superuser=True).order_by('username')
    notifications = Notification.objects.order_by('-created_at')
    timetables = Timetable.objects.order_by('-uploaded_at')
    maintenance_requests = MaintenanceRequest.objects.order_by('-created_at')

    # 🆕 Count users by role
    student_count = Profile.objects.filter(role='student').count()
    teacher_count = Profile.objects.filter(role='teacher').count()
    admin_count = Profile.objects.filter(role='admin').count()

    return render(request, 'myapp/admin_dashboard.html', {
        'users': users,
        'notifications': notifications,
        'timetables': timetables,
        'maintenance_requests': maintenance_requests,
       # 'student_count': student_count,
       # 'teacher_count': teacher_count,
       # 'admin_count': admin_count,
    })
@login_required
def admin_dashboard(request):
    users = User.objects.all()
    announcements = Announcement.objects.all()
    timetables = Timetable.objects.all()
    notifications = Notification.objects.all()
    maintenance_requests = MaintenanceRequest.objects.all()

    schedules = ClassSchedule.objects.all().order_by('date', 'start_time')  # Add this

    context = {
        'users': users,
        'announcements': announcements,
        'timetables': timetables,
        'notifications': notifications,
        'maintenance_requests': maintenance_requests,
        'schedules': schedules,  # Pass it here
    }
    return render(request, 'myapp/admin_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    if request.user.profile.role != 'teacher':
        messages.error(request, "Access denied.")
        return redirect('login')

    users = User.objects.exclude(is_superuser=True).exclude(profile__role='teacher').order_by('username')

    timetables = Timetable.objects.order_by('-uploaded_at')
    notifications = Notification.objects.filter(created_by=request.user).order_by('-created_at')
    maintenance_requests = MaintenanceRequest.objects.order_by('-created_at')
    service_bookings = ServiceBooking.objects.filter(student=request.user).order_by('-date')

    return render(request, 'myapp/teacher_dashboard.html', {
        'users': users,  # 🔥 Don't forget to pass users if you are using it in template
        'timetables': timetables,
        'notifications': notifications,
        'maintenance_requests': maintenance_requests,
         'service_bookings': service_bookings,
    })



@login_required
def student_dashboard(request):
    if request.user.profile.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('login')
    users = User.objects.exclude(is_superuser=True).exclude(profile__role='teacher').order_by('username')
    notifications = Notification.objects.filter(visibility='public').order_by('-created_at')
    timetables = Timetable.objects.order_by('-uploaded_at')
    maintenance_requests = MaintenanceRequest.objects.order_by('-created_at')
    class_schedules = ClassSchedule.objects.filter(students=request.user).order_by('date', 'start_time')
    service_bookings = ServiceBooking.objects.filter(student=request.user).order_by('-date')

    return render(request, 'myapp/student_dashboard.html', {
        'notifications': notifications,
        'timetables': timetables,
        'maintenance_requests': maintenance_requests,
        'class_schedules': class_schedules,  # Pass to template
        'service_bookings': service_bookings,
    })


@login_required
def maintenance_dashboard(request):
    if request.user.profile.role != 'maintenance':
        messages.error(request, "Access denied.")
        return redirect('login')

    maintenance_requests = MaintenanceRequest.objects.filter(
        Q(assigned_to=request.user) | Q(assigned_to__isnull=True)
    ).order_by('-created_at')

    return render(request, 'myapp/maintenance_dashboard.html', {
        'maintenance_requests': maintenance_requests,
    })


@login_required
def create_user(request):
    if request.method == 'POST' and request.user.profile.role == 'admin':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role     = request.POST.get('role')

        user = User.objects.create_user(username=username, password=password)
        user.profile.role = role
        user.profile.save()

        messages.success(request, f"User '{username}' ({role}) created successfully.")
    return redirect('admin_dashboard')


@login_required
def create_timetable(request):
    if request.method == 'POST' and request.user.profile.role in ['admin', 'teacher']:
        uploaded_file = request.FILES.get('file')
        title = request.POST.get('title')  # 🆕 New Field

        if uploaded_file and title:
            Timetable.objects.create(
                uploaded_by=request.user,
                file=uploaded_file,
                title=title  # 🆕 Save title
            )
            messages.success(request, "Timetable uploaded successfully.")
        else:
            messages.error(request, "All fields are required.")
    return redirect('admin_dashboard' if request.user.profile.role == 'admin' else 'teacher_dashboard')



@login_required
def create_notification(request):
    if request.method == 'POST' and request.user.profile.role in ['admin', 'teacher']:
        message_text = request.POST.get('message')
        if message_text:
            Notification.objects.create(
                message=message_text,
                created_by=request.user,
                visibility='public'
            )
            messages.success(request, "Notification created successfully.")
        else:
            messages.error(request, "Notification message cannot be empty.")
    return redirect('teacher_dashboard')

@login_required
def edit_notification(request, notif_id):
    notification = get_object_or_404(Notification, id=notif_id)

    if request.user.profile.role == 'teacher':
        if notification.created_by != request.user:
            messages.error(request, "You can only edit your own notifications.")
            return redirect('teacher_dashboard')
    elif request.user.profile.role == 'admin':
        if notification.created_by != request.user:
            messages.error(request, "You can only edit your own notifications.")
            return redirect('admin_dashboard')
    else:

        messages.error(request, "Access denied.")
        return redirect('login')
    



    if request.method == 'POST':
        message_text = request.POST.get('message')
        visibility = request.POST.get('visibility', 'public')
        if message_text:
            notification.message = message_text
            notification.visibility = visibility
            notification.save()
            messages.success(request, "Notification updated successfully.")
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "Notification message cannot be empty.")

    return render(request, 'myapp/edit_notification.html', {
        'notification': notification
    })

@login_required
def delete_notification(request, notif_id):
    notification = get_object_or_404(Notification, id=notif_id)
    user_role = request.user.profile.role

    if user_role == 'admin':
        # Admin can delete any notification
        notification.delete()
        messages.success(request, "Notification deleted successfully.")
        return redirect('admin_dashboard')
    elif user_role == 'teacher':
        # Teacher can delete only their own notifications
        if notification.created_by == request.user:
            notification.delete()
            messages.success(request, "Notification deleted successfully.")
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "You can only delete your own notifications.")
            return redirect('teacher_dashboard')
    else:
        messages.error(request, "Access denied.")
        return redirect('login')



@login_required
def create_maintenance_request(request):
    if request.method == 'POST' and request.user.profile.role in ['student', 'teacher', 'admin']:
        message = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()

        if message:
            MaintenanceRequest.objects.create(
                requester=request.user,
                message=message,
                location=location if location else None
            )
            messages.success(request, "Maintenance request submitted successfully.")
        else:
            messages.error(request, "Description cannot be empty.")
    return redirect('student_dashboard' if request.user.profile.role == 'student' else (
                    'teacher_dashboard' if request.user.profile.role == 'teacher' else 'admin_dashboard'))


# Adding the 'request_maintenance' view:
@login_required
def request_maintenance(request):
    """ Handles the display and submission of maintenance requests. """
    if request.method == 'POST' and request.user.profile.role in ['student', 'teacher', 'admin']:
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()

        if description:
            MaintenanceRequest.objects.create(
                requester=request.user,
                message=description,
                location=location if location else None
            )
            messages.success(request, "Maintenance request submitted successfully.")
        else:
            messages.error(request, "Description cannot be empty.")
    
    # Return to the dashboard based on role
    return redirect('student_dashboard' if request.user.profile.role == 'student' else (
                    'teacher_dashboard' if request.user.profile.role == 'teacher' else 'admin_dashboard'))


@login_required
def user_profile(request):
    return render(request, 'myapp/profile.html', {
        'user': request.user,
        'role': request.user.profile.role
    })


@login_required
def post_announcement_comment(request, ann_id):
    announcement = get_object_or_404(Announcement, pk=ann_id)
    if request.method == 'POST' and request.user.profile.role == 'student':
        text = request.POST.get('comment', '').strip()
        if text:
            AnnouncementComment.objects.create(
                user=request.user,
                announcement=announcement,
                comment=text
            )
            messages.success(request, "Comment posted.")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect('student_dashboard')


def home(request):
    if request.user.is_authenticated:
        role = getattr(request.user.profile, 'role', None)
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'teacher':
            return redirect('teacher_dashboard')
        elif role == 'student':
            return redirect('student_dashboard')
        elif role == 'maintenance':
            return redirect('maintenance_dashboard')
        else:
            return redirect('dashboard')

    return render(request, 'myapp/home.html')

def send_alert_to_maintenance(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        # Logic for notifying the maintenance team can go here
        messages.success(request, 'Alert sent to maintenance team successfully.')
        return redirect('admin_dashboard')  # Redirect back to the admin dashboard
    return render(request, 'admin_dashboard.html')




@login_required
def delete_maintenance_request(request, req_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=req_id)
    if request.method == 'POST':
        maintenance_request.delete()
        messages.success(request, "Maintenance request deleted successfully.")
        return redirect('admin_dashboard')
    
    # Auto-delete without confirmation
    maintenance_request.delete()
    messages.success(request, "Maintenance request deleted successfully.")
    return redirect('admin_dashboard')

@login_required
def edit_maintenance_request(request, request_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id)

    # Only allow the requester or admin to edit
    if request.user != maintenance_request.requester and request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to edit this request.")
        return redirect('dashboard')

    if request.method == 'POST':
        message = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()

        if message:
            maintenance_request.message = message
            maintenance_request.location = location
            maintenance_request.save()
            messages.success(request, "Maintenance request updated successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Description cannot be empty.")

    return render(request, 'myapp/edit_maintenance_request.html', {
        'maintenance_request': maintenance_request
    })




@login_required
def create_maintenance_request(request):
    if request.method == 'POST' and request.user.profile.role in ['student', 'teacher', 'admin']:
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()

        if description:
            MaintenanceRequest.objects.create(
                requester=request.user,
                message=description,
                location=location
            )
            messages.success(request, "Maintenance request submitted successfully.")
        else:
            messages.error(request, "Description cannot be empty.")
    
    return redirect('student_dashboard' if request.user.profile.role == 'student' else (
                    'teacher_dashboard' if request.user.profile.role == 'teacher' else 'admin_dashboard'))

@login_required
def delete_maintenance_request(request, req_id):
    maintenance_request = get_object_or_404(MaintenanceRequest, id=req_id)

    if request.user.profile.role == 'admin':
        # Admins can delete any maintenance request
        maintenance_request.delete()
        messages.success(request, "Maintenance request deleted successfully.")
        return redirect('admin_dashboard')

    elif request.user == maintenance_request.requester:
        # Students and Teachers can delete their own maintenance requests
        maintenance_request.delete()
        messages.success(request, "Maintenance request deleted successfully.")
        if request.user.profile.role == 'student':
            return redirect('student_dashboard')
        elif request.user.profile.role == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('dashboard')

    else:
        messages.error(request, "You don't have permission to delete this request.")
        return redirect('dashboard')


@login_required
def edit_maintenance_request_modal(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id)

        # Only allow owner or admin
        if request.user != maintenance_request.requester and request.user.profile.role != 'admin':
            messages.error(request, "You don't have permission to edit this request.")
            return redirect('admin_dashboard')

        message = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()

        if message:
            maintenance_request.message = message
            maintenance_request.location = location
            maintenance_request.save()
            messages.success(request, "Maintenance request updated successfully.")
        else:
            messages.error(request, "Description cannot be empty.")

    return redirect('admin_dashboard')

@login_required
def create_class_schedule(request):
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        
        if form.is_valid():
            class_schedule = form.save()  # Simple save — no need for commit=False if handled properly in form
            
            messages.success(request, 'Class schedule created successfully.')
            return redirect('view_class_schedules')
        else:
            messages.error(request, 'There were errors in your form. Please correct them.')
    else:
        form = ClassScheduleForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'myapp/class_schedule_create.html', context)


# View all class schedules (different for students/teachers/admins)
@login_required
def view_class_schedules(request):
    user = request.user

    if hasattr(user, 'profile'):
        if user.profile.role == 'teacher':
            # Teachers can view the schedules they are teaching
            schedules = ClassSchedule.objects.filter(teacher=user).order_by('date', 'start_time')
        elif user.profile.role == 'student':
            # Students can view the schedules for their enrolled classes
            schedules = ClassSchedule.objects.filter(students=user).order_by('date', 'start_time')
        elif user.profile.role == 'admin':
            # Admin can view all schedules
            schedules = ClassSchedule.objects.all().order_by('date', 'start_time')
        else:
            schedules = ClassSchedule.objects.none()  # If the role doesn't match, return no schedules
    else:
        schedules = ClassSchedule.objects.none()  # If no profile exists, return no schedules

    context = {'schedules': schedules}
    return render(request, 'myapp/list.html', context)

# Edit an existing class schedule
@login_required
def edit_class_schedule(request, schedule_id):
    schedule = get_object_or_404(ClassSchedule, id=schedule_id)

    if request.user != schedule.teacher and request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to edit this schedule.")
        return redirect('view_class_schedules')

    if request.method == 'POST':
        schedule.subject_name = request.POST.get('subject_name')
        schedule.room = request.POST.get('room')
        schedule.date = request.POST.get('date')
        schedule.start_time = request.POST.get('start_time')
        schedule.end_time = request.POST.get('end_time')
        
        teacher_id = request.POST.get('teacher')
        if teacher_id:
            schedule.teacher = get_object_or_404(User, id=teacher_id)

        student_ids = request.POST.getlist('students')
        schedule.students.set(student_ids)

        schedule.save()
        messages.success(request, 'Class schedule updated successfully.')
        return redirect('view_class_schedules')

    teachers = User.objects.filter(profile__role='teacher')
    students = User.objects.filter(profile__role='student')

    context = {
        'schedule': schedule,
        'teachers': teachers,
        'students': students,
    }
    return render(request, 'myapp/edit.html', context)


# Delete a class schedule
@login_required
def delete_class_schedule(request, schedule_id):
    schedule = get_object_or_404(ClassSchedule, id=schedule_id)

    if request.user != schedule.teacher and request.user.profile.role != 'admin':
        messages.error(request, "You don't have permission to delete this schedule.")
        return redirect('view_class_schedules')

    schedule.delete()
    messages.success(request, "Class schedule deleted successfully.")
    return redirect('view_class_schedules')

@login_required
def book_service(request):
    if request.user.profile.role != 'student':
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            booking.save()
            return redirect('student_dashboard')
    else:
        form = ServiceBookingForm()
    
    return render(request, 'myapp/book_service.html', {'form': form})

@login_required
def view_booked_services(request):
    # Retrieve all service bookings
    bookings = ServiceBooking.objects.all()
    
    return render(request, 'myapp/view_booked_services.html', {
        'bookings': bookings
    })


def system_overview(request):
    student_count = Profile.objects.filter(role='Student').count()
    teacher_count = Profile.objects.filter(role='Teacher').count()
    admin_count = Profile.objects.filter(role='Admin').count()

    # Prepare data for Chart.js
    chart_data = {
        'labels': ['Students', 'Teachers', 'Admins'],
        'counts': [student_count, teacher_count, admin_count]
    }

    return render(request, 'myapp/overview_dashboard.html', {
        'student_count': student_count,
        'teacher_count': teacher_count,
        'admin_count': admin_count,
        'chart_data': chart_data
    })
@login_required
@user_passes_test(is_teacher)
def create_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            test = form.save(commit=False)
            test.created_by = request.user
            test.save()
            messages.success(request, "Test created successfully.")
            return redirect('teacher_tests')
    else:
        form = TestForm()
    return render(request, 'tests/create_test.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def edit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, created_by=request.user)
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES, instance=test)
        if form.is_valid():
            form.save()
            messages.success(request, "Test updated.")
            return redirect('teacher_tests')
    else:
        form = TestForm(instance=test)
    return render(request, 'tests/edit_test.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def delete_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, created_by=request.user)
    if request.method == 'POST':
        test.delete()
        messages.success(request, "Test deleted.")
        return redirect('teacher_tests')
    return render(request, 'tests/delete_test.html', {'test': test})


@login_required
@user_passes_test(is_teacher)
def teacher_tests(request):
    tests = Test.objects.filter(created_by=request.user)
    return render(request, 'tests/teacher_tests.html', {'tests': tests})

@login_required
@user_passes_test(is_student)
def available_tests(request):
    tests = Test.objects.filter(due_date__gte=timezone.now())
    submitted_ids = TestSubmission.objects.filter(student=request.user).values_list('test_id', flat=True)
    return render(request, 'tests/available_tests.html', {
        'tests': tests,
        'submitted_ids': submitted_ids
    })


@login_required
@user_passes_test(is_student)
def submit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    if TestSubmission.objects.filter(test=test, student=request.user).exists():
        messages.warning(request, "You have already submitted this test.")
        return redirect('available_tests')

    if request.method == 'POST':
        form = TestSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.test = test
            submission.student = request.user
            submission.save()
            messages.success(request, "Test submitted.")
            return redirect('available_tests')
    else:
        form = TestSubmissionForm()

    return render(request, 'tests/submit_test.html', {'form': form, 'test': test})
