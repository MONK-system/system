from django.urls import path
from . import views 



urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser, name = "logout"),
    path('register/', views.registerPage, name = "register"),
    path('patient/<str:pk>', views.patient, name="patient"),
    
    path('viewDoctor/', views.viewDoctor, name = "viewDoctor"),
    path('addDoctor/', views.addDoctor, name = "addDoctor"),
    
    path('viewPatient/', views.viewPatient, name = "viewPatient"),
    path('addPatient/', views.addPatient, name = "addPatient"),

    path('viewProject/', views.viewProject, name = "viewProject"),
    path('addProject/', views.addProject, name = "addProject"),

    path('viewVitals/', views.viewVitals, name = "viewVitals"),
    #path('addVitals/', views.addVitals, name = "addVitals"),


]