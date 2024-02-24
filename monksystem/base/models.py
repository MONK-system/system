from django.db import models
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Create your models here.



class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)
    name = models.CharField(max_length=50)
    mobile = models.IntegerField()
    specialization = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


class DoctorRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=50, help_text='Required. Add your full name.')
    mobile = forms.IntegerField(help_text='Required. Add a contact number.')
    specialization = forms.CharField(max_length=50, help_text='Required. Add your specialization.')

    class Meta:
        model = User
        fields = ['username', 'name', 'mobile', 'specialization', 'password1', 'password2']

class Patient(models.Model):
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    mobile = models.IntegerField(null=True)
 
    def __str__(self):
        return self.name

class Project(models.Model):
    rekNummer = models.TextField(null = True, blank = True) # Description of appointment. Makes sure the values can be left blank. 
    description = models.TextField(null = True, blank = True) # Description of appointment. Makes sure the values can be left blank. 
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE) # When doctor is deleted, appointment is also deleted.
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE) # When patient is deleted, appointment is also deleted.
    updated = models.DateTimeField(auto_now = True) # Takes a snapshot of anytime the table (model instance) is updated. Takes a timestamp every time appointment is updated.
    created = models.DateTimeField(auto_now_add = True) # Takes a timestamp of when the instance was created.
    
    def __str__(self):
        return self.doctor.name+"--"+self.patient.name
    
class Vitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE) # When patient is deleted, appointment is also deleted.
    description = models.TextField(null = True, blank = True) # Description of appointment. Makes sure the values can be left blank. 
    heartRate = models.IntegerField(null=True)
    oxygen = models.IntegerField(null=True)
    bodyTemperature = models.IntegerField(null=True)
    respirationRate = models.IntegerField(null=True)
    bloodPressure = models.IntegerField(null=True)
    updated = models.DateTimeField(auto_now = True) # Takes a snapshot of anytime the table (model instance) is updated. Takes a timestamp every time appointment is updated.
    created = models.DateTimeField(auto_now_add = True) # Takes a timestamp of when the instance was created.
    
    def __str__(self):
        return self.patient.name


# Model for the files
class File(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='nihon_kohden_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model for file claims
class FileClaim(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.title} claimed by {self.doctor.name}"