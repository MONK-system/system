from django.db import models

# Create your models here.

class Doctor(models.Model):
    name = models.CharField(max_length=50)
    mobile = models.IntegerField()
    specialization = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

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
