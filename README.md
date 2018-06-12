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

1. setup database **(only once)**
    - for simple database setup:

    `bash scripts/create_user_db.sh`

    - if you want to specify a string as user

    `bash USER=username scripts/create_user_db.sh`

2. install and run project:
    - run `make prepare-dev` to install all relevant packages
      (it also runs `make venv` internally (this will create a virtualenv inside the project).) **(run only once)**
    - run command `make lint` to check for any errors which can cause problems
    - run command `make setup` - this will install all the dependencies from `requirements.txt` file)
    - create and setup `geodjango/settings_secret.py` with settings based on the template in the same folder
    - run command `make run` - this will makemigrations and migrate into database (needs to be looked into) and run the app on port 8000)
