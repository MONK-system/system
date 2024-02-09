from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


patients = [
    {"id" : 1, "name" : "Aliaan"},
    {"id" : 2, "name" : "Jonathan"},
    {"id" : 3, "name" : "Sondre"},

]

def home(request):
    context = {"patients" : patients}
    return render(request, 'base/home.html', context)

def patient(request):
    return render(request, 'base/patient.html')