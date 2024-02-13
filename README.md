# MONK - System

Linux architecture and application for management and access control of Nihon-Kohden MFER data.

## Cloning the repository 

--> Clone the repository using the command below: 

````
git clone https://github.com/MONK-system/system.git
````

## Create a virtual environment (Not mandatory, but recommended) 

--> installs the virutalenv first
````
pip install virtualenv
````

--> Then we create our virtual environment
````
virutalenv {your environment name}
````

--> Activate the virtual environment: 
````
{your environment name}\scripts\activate
````


## Install the requirements: 
````
pip install django
````


## Running the application

--> To run the app, we use this command in the terminal: 

````
python manage.py runserver
````

### Then, the development server will be started at : http://127.0.0.1:8000/
