from django import forms
from .models import ClassSchedule,ServiceBooking,Test, TestSubmission

class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['subject_name', 'teacher', 'students', 'room', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'students': forms.CheckboxSelectMultiple(),
        }

class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = ['service_type', 'room_or_person', 'date', 'start_time', 'end_time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'room_or_person': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'service_type': 'Type of Service',
            'room_or_person': 'Room / Person',
            'reason': 'Reason (Optional)',
        }



class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'due_date', 'subject', 'attached_file']


class TestSubmissionForm(forms.ModelForm):
    class Meta:
        model = TestSubmission
        fields = ['submitted_text', 'submitted_file']
