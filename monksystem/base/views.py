import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
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
from monklib import get_header
from .utils import parse_mwf_file
from datetime import datetime



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
    is_MFER_file = file.file.name.endswith('.MWF')
    is_text_file = file.file.name.endswith('.txt')

    if is_MFER_file:
        try:
            content = get_header(file.file.path)
        except Exception as e:
            content = f"Error reading file: {e}"    
    elif is_text_file:
        try:
            with open(file.file.path, 'r') as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"
    else:
        content = None

    context = {'file': file, 'content': content, 'is_text_file': is_text_file, 'is_MFER_file': is_MFER_file}
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
            messages.success(request, f'Logged in successfully as {user.username}.') 
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

@login_required
def viewDoctor(request):
    
    doctors = Doctor.objects.all()
    
    context = {'doctors' : doctors}
    return render(request,'base/view_doctor.html', context)
    
@login_required
def viewPatient(request):
    
    patients = Patient.objects.all()
    
    context = {'patients' : patients}
    return render(request,'base/view_patient.html', context)
    
#@login_required
#def viewProject(request):
#    
#    projects = Project.objects.all()
#    
#    context = {'projects' : projects}
#    return render(request,'base/view_project.html', context)
    
@login_required
def viewProject(request):
    # Check if the logged-in user is associated with a Doctor instance
    try:
        doctor = request.user.doctor
        # Filter projects where the current user's doctor instance is in the project's doctors
        projects = Project.objects.filter(doctors=doctor)
    except Doctor.DoesNotExist:
        # If the user does not have an associated Doctor instance, return an empty project list
        projects = Project.objects.none()
    
    context = {'projects': projects}
    return render(request, 'base/view_project.html', context)
    


@login_required
def viewVitals(request):
    
    vitals = Vitals.objects.all()

    context = {'vitals' : vitals}
    return render(request,'base/view_vitals.html', context)

@login_required
def addDoctor(request):
    
    if request.method == "POST":
        name = request.POST['name']
        contact = request.POST['contact']
        specialization = request.POST['specialization']
        
        Doctor.objects.create(name=name, mobile=contact, specialization = specialization)
        messages.success(request, "Doctor added successfully.")
        return redirect("viewDoctor")
    
    return render(request, 'base/add_doctor.html')


@login_required
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

@login_required
def addProject(request):
    if request.method == "POST":
        rekNummer = request.POST.get('rekNummer')
        description = request.POST.get('description')
        doctors_ids = request.POST.getlist('doctors')  
        patients_ids = request.POST.getlist('patients')  

        # Create project instance
        project = Project.objects.create(rekNummer=rekNummer, description=description)

        # Set doctors and patients for the project
        project.doctors.set(Doctor.objects.filter(id__in=doctors_ids))
        project.patients.set(Patient.objects.filter(id__in=patients_ids))

        messages.success(request, "Project added successfully.")
        return redirect("viewProject")
    
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
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
    form = FileForm()
    if request.method == 'POST' and 'submitted' in request.POST:
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "File uploaded successfully.")
            return redirect('home')
        else:
            # Check explicitly for empty title or file when the form is submitted
            if not request.FILES.get('file') or not request.POST.get('title'):
                messages.error(request, "Both title and file are required.")
            else:
                # Handle other form errors
                messages.error(request, "Please correct the error below.")

    return render(request, 'base/upload_file.html', {'form': form})


@login_required
def claim_file(request, file_id):
    # Attempt to claim the file
    file_to_claim = get_object_or_404(File, id=file_id)

    # Check if the file has already been claimed
    if FileClaim.objects.filter(file=file_to_claim).exists():
        messages.error(request, "This file has already been claimed.")
        return redirect('home')

    try:
        doctor = request.user.doctor
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor. Only doctors can claim files.")
        return redirect('home')

    # Proceed with claiming the file
    FileClaim.objects.create(doctor=doctor, file=file_to_claim)
    messages.success(request, "File claimed successfully.")

    # Process the file if it is an MWF file
    if file_to_claim.file.name.endswith('.MWF'):
        try:
            # Use the monklib module to get the header data
            header = get_header(file_to_claim.file.path)

            # Extract patient information from the header
            patient_id = header.patientID
            patient_name = header.patientName
            patient_sex = header.patientSex
            birth_date_str = header.birthDateISO

            # Parse the birth date if it's not 'N/A' and in the expected format
            if birth_date_str != 'N/A':
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    birth_date = None
            else:
                birth_date = None

            # Check if the patient already exists
            if not Patient.objects.filter(patient_id=patient_id).exists():
                # Create a new patient object with the extracted data
                Patient.objects.create(
                    patient_id=patient_id,
                    name=patient_name,
                    gender=patient_sex,
                    birth_date=birth_date,
                    file=file_to_claim
                )
                messages.success(request, f"Patient with ID {patient_id} was successfully created.")
            else:
                messages.info(request, f"A patient with ID {patient_id} already exists.")
        except Exception as e:
            messages.error(request, f"An error occurred while processing the file: {str(e)}")
    else:
        messages.error(request, "Unsupported file format. Only .MWF files are accepted.")

    # Redirect back to the home page
    return redirect('home')


@login_required
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
    