from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)
    name = models.CharField(max_length=50)
    mobile = models.IntegerField()
    specialization = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


# Model for the files
class File(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='nihon_kohden_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Patient(models.Model):
    patient_id = models.CharField(max_length=50, unique=True, null=True)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    birth_date = models.DateField(null=True, blank=True)
    file = models.ForeignKey(File, null=True, on_delete=models.CASCADE, related_name='patients')

    def __str__(self):
        return f"{self.patient_id} - {self.name}"



class Project(models.Model):
    rekNummer = models.TextField(null = True, blank = True) 
    description = models.TextField(null = True, blank = True) # Description of project. Makes sure the values can be left blank. 
    
    doctors = models.ManyToManyField(Doctor, related_name='projects')
    patients = models.ManyToManyField(Patient, related_name='projects')
    
    updated = models.DateTimeField(auto_now = True) # Takes a snapshot of anytime the table (model instance) is updated. Takes a timestamp every time appointment is updated.
    created = models.DateTimeField(auto_now_add = True) # Takes a timestamp of when the instance was created.
    
    def __str__(self):
        return self.rekNummer
    
class Vitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE) 
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


# Model for file claims
class FileClaim(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.title} claimed by {self.doctor.name}"