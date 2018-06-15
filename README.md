# gtfsintegrate

This is the main GSOC project repository.

### Requirements
This application requires several tools to run it. These tools are:
- GDAL https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/geolibs/#gdal
- GEOS https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/geolibs/#geos
- repository code https://github.com/sriks123/gtfsintegrate.
- `virtualenv` / `postgres` (https://www.postgresql.org/download/) + `postgis` (https://postgis.net/install/)

### How to start

0. clone the project with
    
```git clone git@github.com:sriks123/gtfsintegrate.git```

     Extra steps if you want to contribute back:
     ```git config --global --edit```
     ```ssh-keygen -t rsa -b 4096 -C "your@email.domain"```
     ```cat ~/.ssh/id_rsa.pub```

     Copy this to your github.com settings, add ssh key

1. setup database **(only once)**
    username is the existing postgres user which is already created
    `bash scripts/create_user_db.sh username`

2. install and run project:
    - ```sudo apt install make```
    - run `make prepare-dev` to install all relevant packages
      (it also runs `make venv` internally (this will create a virtualenv inside the project).) **(run only once)**
    - run command `make lint` to check for any errors which can cause problems
    - run command `make setup` - this will install all the dependencies from `requirements.txt` file)
    - create and setup `geodjango/settings_secret.py` with settings based on the template in the same folder
    - run command `make run` - this will makemigrations and migrate into database (needs to be looked into) and run the app on port 8000)
