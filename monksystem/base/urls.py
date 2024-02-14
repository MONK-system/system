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
    path('viewPatient/', views.viewPatient, name = "viewPatient"),
    path('viewAppointment/', views.viewAppointment, name = "viewAppointment"),

]