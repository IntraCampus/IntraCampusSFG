from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('maintenance', 'Maintenance'),
    )

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Announcement(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('maintenance', 'Maintenance'),
        ('all', 'All Users'),
    )

    title        = models.CharField(max_length=255)
    content      = models.TextField()
    attachment   = models.FileField(upload_to='announcements/', blank=True, null=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    created_at   = models.DateTimeField(auto_now_add=True)
    target_role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default='all')

    def __str__(self):
        return self.title


class AnnouncementComment(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='comments')
    comment      = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.announcement.title}"


class Timetable(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, default='Default Title')

    file        = models.FileField(upload_to='timetables/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Timetable by {self.uploaded_by.username if self.uploaded_by else 'Unknown'} at {self.uploaded_at}"



class Notification(models.Model):
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    message    = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')

    def __str__(self):
        return f"Notification: {self.message[:50]}"


class Comment(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='comments')
    comment      = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Notification"


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = (
        ('Alert', 'Alert'),         # Admin-sent alerts
        ('Pending', 'Pending'),     # Student/teacher created
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    )

    requester    = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    message      = models.TextField()
    location     = models.CharField(max_length=255, blank=True, null=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_to  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request by {self.requester.username} - {self.status}"
    
class ClassSchedule(models.Model):
    subject_name = models.CharField(max_length=255)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'profile__role': 'teacher'},
        related_name='scheduled_classes'
    )
    students = models.ManyToManyField(
        User,
        limit_choices_to={'profile__role': 'student'},
        related_name='class_schedules'
    )
    room = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True) 
    


    def __str__(self):
        return f"{self.subject_name} - {self.date} ({self.start_time} to {self.end_time})"
 
class ServiceBooking(models.Model):
    SERVICE_TYPE_CHOICES = (
        ('study_room', 'Study Room'),
        ('appointment', 'Appointment'),
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'student'},
        related_name='service_bookings'
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    room_or_person = models.CharField(max_length=255, help_text="Room number or Person to meet")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_type} booking by {self.student.username} on {self.date}"

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'teacher'},
        related_name='created_tests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    subject = models.CharField(max_length=100)
    attached_file = models.FileField(upload_to='tests/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.created_by.username}"


class TestSubmission(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'student'},
        related_name='test_submissions'
    )
    submitted_file = models.FileField(upload_to='test_submissions/', blank=True, null=True)
    submitted_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username}'s submission for {self.test.title}"
