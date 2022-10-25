## Description of the project

&nbsp;

Prodject **YaTube** Social network for publishing diaries. Developed according to the classical MVP architecture. Uses pagination and post caching. Registration is implemented with data verification, password change and recovery via mail. Written tests that check the operation of the service

&nbsp;

## How to run project(Windows) :

&nbsp;

### Clone a repository:

```
git clone https://github.com/Gollum959/hw05_final
```

### Create and activate virtual environment:

```
py -m venv venv | python -m venv venv | python3 -m venv venv
```

```
source venv/scripts/activate
```

### Install dependencies from a file requirements.txt:

```
pip install -r requirements.txt
```

### Make migrations:

```
python manage.py migrate
```

### Run project:

```
python manage.py runserver
```

## Authors
[Aleksandr Alekseev](https://github.com/Gollum959/)

## Technologies

Project is created with:
* Python 3.7
* SqLite
* Django 2.2.16
