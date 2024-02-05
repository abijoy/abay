# abay

A simple bidding platform on products

Live Demo: https://spike87.pythonanywhere.com/

### How to run this project

### Clone the repository

`https://github.com/abijoy/abay.git`

`cd abay`

### Install the required packages

First create and activate virtual environment then install the required packages.

`python3 -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

### Set up the .env file

`cat .env.example > .env`

In your `.env` set the following environment variables:

DJANGO SPECIFIC CONFIG

- `SECRET_KEY`: add a arbitrary secret key needed by django
- `DEBUG`: set either `True` or `False`

EMAIL CONFIG

- `EMAIL_HOST`: Your email host(i.e. smtp.gmail.com )
- `EMAIL_PORT`: 587
- `EMAIL_HOST_USER`: Your email address.
- `EMAIL_HOST_PASSWORD`: Your email password.

Carefully modify your `.env` file.

### Now perform database migration

`python manage.py migrate`

## Run the server

`python manage.py runserver`
