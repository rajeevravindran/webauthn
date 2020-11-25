# Passwordless Authentication using WebAuthn

This project serves as the backend for a WebAuthn client. The client side Angular project can be found [here](https://github.com/rajeevravindran/csec604termprojectwebauthn-frontend)

A demo implementation can be found [here](https://csec-604-crypto-term-project.rajeevkr.me/) 

## Setup Instructions

Requires Python 3.7+

```commandline
(termprojectwebauthn) user@laptop:~$ pip install -r requirements.txt
```

Create `termprojectwebauthn\local_settings.py` file and add the following
```python
## You can generate a secret by the executing the following on a commandline : 
## python3 -c "from django.core.management.utils import get_random_secret_key;get_random_secret_key()"
SECRET_KEY = 'set newly generated key here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

## Start Development Server
```commandline
(termprojectwebauthn) user@laptop:~$ python manage.py migrate
(termprojectwebauthn) user@laptop:~$ python manage.py createsuperuser
(termprojectwebauthn) user@laptop:~$ python manage.py runserver
```