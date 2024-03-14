import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from .models import Patient, Doctor, Project, Vitals, File, FileClaim
from django.contrib import messages
from .forms import FileForm, DoctorRegistrationForm  # Import the FileForm
from django.conf import settings
from django.core.files import File as DjangoFile
from pathlib import Path


def home(request):
    patients  = Patient.objects.all()
    context = {"patients" : patients}
    return render(request, 'base/home.html', context)

def patient(request, pk):
    patient = Patient.objects.get(id=pk)
    context = {'patient':patient}
    return render(request, 'base/patient.html', context)

def doctor(request, pk):
    doctor = Doctor.objects.get(id=pk)
    context = {'doctor':doctor}
    return render(request, 'base/doctor.html', context)

def project(request, pk):
    project = Project.objects.get(id=pk)
    context = {'project':project}
    return render(request, 'base/project.html', context)

def about(request):
    return render(request, "base/about.html")

def contact(request):
    return render(request, "base/contact.html")


def file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    try:
        claim = FileClaim.objects.get(file=file, doctor__user=request.user)
    except FileClaim.DoesNotExist:
        # If the file is not claimed by the current user, return an error or redirect
        return HttpResponseForbidden("You do not have permission to view this file.")

    # If the user has claimed the file, proceed with showing the content
    is_text_file = file.file.name.endswith('.txt')
    
    if is_text_file:
        try:
            with open(file.file.path, 'r') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"
    else:
        content = None

    context = {'file': file, 'content': content, 'is_text_file': is_text_file}
    return render(request, 'base/file.html', context)


# Function for logging in a user
def loginPage(request):
    
    # sets the variable page to specify that this is a login page, it is passed into the context variable, and used in the html to run the correct code.
    page = 'login'
    
    # If the user is already logged in and tries to click on the login button again, they will just get redirected to home instead. 
    if request.user.is_authenticated:
        return redirect('home')
    
    # Checks if a POST request was sent. 
    if request.method == 'POST':
        # Get the username and password from the data sent in the POST request. 
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        # Checks if the user exists with a try catch block. 
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        
        # Gets user object based on username and password.
        # Authenticate method will either give us an error or return back a user that matches the credentials (username and password).
        user = authenticate(request, username=username, password=password)
        
        # Logs the user in if there is one, and returns home. 
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')  # Add success message here
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
                
    
    context = {'page' : page}
    return render(request, 'base/login_register.html', context)    

# Function for logging out a user. 
def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    # else is used in the html, so no need for a page variable here. 
    #form = UserCreationForm()
    form = DoctorRegistrationForm()

    # Check if method is a POST request
    if request.method == 'POST':
        #form = UserCreationForm(request.POST) # passes in the data: username and password into user creation form
        form = DoctorRegistrationForm(request.POST)

        # Checks if the form is valid
        if form.is_valid():
            user = form.save(commit=False) # saving the form, freezing it in time. If the form is valid, the user is created and we want to be able to access it right away. This is why we set commit = False
            user.username = user.username.lower() # Now that the user is created, we can access their credentials, like username and password. We lowercase the username of the user. 
            user.save() # saves the user. 
            
            # Now, use the extra fields to create a Doctor instance
            Doctor.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                mobile=form.cleaned_data.get('mobile'),
                specialization=form.cleaned_data.get('specialization'),
            ) 
            
            login(request, user) # logs the user in.
            return redirect('home') # sends the user back to the home page.
        else: 
            messages.error(request, 'An error occurred during registration')
            
    context = {'form' : form}
    return render(request,'base/login_register.html', context)


def viewDoctor(request):
    
    doctors = Doctor.objects.all()
    
    context = {'doctors' : doctors}
    return render(request,'base/view_doctor.html', context)
    

def viewPatient(request):
    
    patients = Patient.objects.all()
    
    context = {'patients' : patients}
    return render(request,'base/view_patient.html', context)
    

def viewProject(request):
    
    projects = Project.objects.all()
    
    context = {'projects' : projects}
    return render(request,'base/view_project.html', context)
    

def viewVitals(request):
    
    vitals = Vitals.objects.all()

    context = {'vitals' : vitals}
    return render(request,'base/view_vitals.html', context)


def addDoctor(request):
    
    if request.method == "POST":
        name = request.POST['name']
        contact = request.POST['contact']
        specialization = request.POST['specialization']
        
        Doctor.objects.create(name=name, mobile=contact, specialization = specialization)
        messages.success(request, "Doctor added successfully.")
        return redirect("viewDoctor")
    
    return render(request, 'base/add_doctor.html')


def addPatient(request):
    
    if request.method == "POST":
        name = request.POST['name']
        gender = request.POST['gender']
        address = request.POST['address']
        mobile = request.POST['mobile']
        
        Patient.objects.create(name=name, gender=gender, address=address, mobile=mobile)
        messages.success(request, "Patient added successfully.")
        return redirect("viewPatient")
    
    return render(request, 'base/add_patient.html')


def addProject(request):
    
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    
    if request.method == "POST":
        rekNummer = request.POST['rekNummer']
        description = request.POST['description']
        d = request.POST['doctor']
        p = request.POST['patient']
        doctor = Doctor.objects.filter(name=d).first()
        patient = Patient.objects.filter(name=p).first()
                
        Project.objects.create(rekNummer = rekNummer, description = description, doctor = doctor, patient = patient)
        messages.success(request, "Project added successfully.")
        return redirect("viewProject")
    
    context = {'doctors' : doctors, 'patients' : patients}
    return render(request, 'base/add_project.html', context)


@login_required
def home(request):
    files = File.objects.all()
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FileForm()
    context = {'files': files, 'form': form}
    return render(request, 'base/home.html', context)


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = FileForm()
    return render(request, 'base/upload_file.html', {'form': form})

@login_required
def claim_file(request, file_id):
    file_to_claim = get_object_or_404(File, id=file_id)

    # Check if the file has already been claimed
    if FileClaim.objects.filter(file=file_to_claim).exists():
        messages.error(request, "This file has already been claimed.")
        return redirect('home')

    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, "You do not have a doctor profile yet. Please create one.")
        return redirect('home')
    
    FileClaim.objects.create(doctor=doctor, file=file_to_claim)
    messages.success(request, "File claimed successfully.")
    return redirect('home')


def import_files(request):
    # Build the directory path dynamically using BASE_DIR
    directory_path = Path(settings.BASE_DIR) / "nihon_kohden_files"
    files_imported = False

    # Check if directory exists before listing files
    if directory_path.exists() and directory_path.is_dir():
        for filename in os.listdir(directory_path):
            file_path = directory_path / filename
            if not File.objects.filter(title=filename).exists():
                with file_path.open('rb') as file:
                    django_file = DjangoFile(file, name=filename)
                    File.objects.create(title=filename, file=django_file)
                    files_imported = True  # Mark as true if at least one file is imported
    else:
        return HttpResponse("The directory does not exist.")

    if not files_imported:
        return HttpResponse("No more files to import.")
    else:
        return HttpResponse("Files imported successfully.")
    