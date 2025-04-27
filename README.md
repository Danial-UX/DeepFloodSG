# DeepFloodSG

## Overview

DeepFlood SG is an AI-powered flood risk prediction model that leverages machine learning, geospatial analysis, and real-time weather data to forecast flood-prone areas. It integrates multiple data sources to provide real-time risk assessments. It empowers authorities and citizens with early warnings and tools for proactive decision-making.

## Features

- User registration and login
- Map showing covered walkways 
- Routes from a start to end destination which avoids flood risk areas / heat-prone areas
- Flood risk prediction 

## Technologies

- Backend: Django, Django REST Framework
- Frontend: React, Axios
- Database: PostgreSQL

## Getting Started

### Clone the repository

Clone the repository to run the program locally.

```bash
git clone 
```

### Database Setup

1. Database: Install PostgreSQL from https://www.postgresql.org/download/.
2. Add to PATH.
3. Create a user for postgres locally. This is the user that django has been configured to as well.
   ```bash
   psql -U postgres
   CREATE USER adminuser WITH PASSWORD 'password';
   CREATE DATABASE deepfloodsg OWNER admin;
   ```

### Backend Setup

1. Backend: Virtual Environment
   Set up a virtual environment in the repository.

   ```
   pip install virtualenv
   python<version> -m venv <virtual-environment-name>
   ```

   To activate the virtual environment:
   On Mac OS:

   ```
   source <virtual-environment-name>/bin/activate
   ```

   On Windows:

   ```
   <virtual-environment-name>/Scripts/activate.bat //In CMD
   <virtual-environment-name>/Scripts/Activate.ps1 //In Powershel
   ```

2. Run the commands below to install dependencies and run the backend server.

   ```
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. Run the following command to insert mock device data into the database.

   ```
   python manage.py populate_db
   ```

4. Run the following command to delete all mock device data from the database.
   ```
   python manage.py clear_db
   ```

### Frontend Setup

```
cd frontend
npm install
npm start
```

## Post-Changes Workflow

### Backend

1. Note that if you make any changes to any models.py, run the following command to flush the changes to the database:

   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

   Restart the Django server to reflect the changes.

2. For models to show up within the Django admin page, you will need to ensure that it is

### Frontend

If any changes are made to the frontend, build and deploy the React app:

```bash
npm run build
npm run deploy
```

## Running Google Maps API

1. Head to: https://developers.google.com/maps and generate your API key.

2.Copy and paste it into .env under REACT_APP_GOOGLE_MAPS_API_KEY (reference .env.example for example .env config)

3.Uncomment line for google maps api key for prod in file MapWindow.js.

## Django Admin Panel Access

1. Create superuser by running `python3 manage.py createsuperuser` in terminal, and `user: admin`, `password: password`
2. Go to admin panel at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
3. Login with `user: superadmin`, `password: password`

## Exposed APIs

### Authentication

1. POST `: /api/account/login/`
2. POST `: /api/account/register/`
3. POST `: /api/account/logout/`

### Device Data Management

1. GET `: /api/devices/getall/`
2. POST `: /api/devices/upload/`
