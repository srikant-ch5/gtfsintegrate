# gtfsintegrate

This is the main GSOC project repository.

### Requirements
This application requires several tools to run it. These tools are:
- GDAL https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/geolibs/#gdal
- GEOS https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/geolibs/#geos
- repository code https://github.com/sriks123/gtfsintegrate.
- `virtualenv` / `postgres` (https://www.postgresql.org/download/) + `postgis` (https://postgis.net/install/)

### How to start

0. clone the project with `git clone git@github.com:sriks123/gtfsintegrate.git`
1. (only once) ... run `make prepare-dev` to install all relevant packages
2. (only once) ... setup database
    - to simply setup database:
    `scripts/create_user_db.sh`
    - if you want to specify a string as user
    `USER=username scripts/create_user_db.sh`
3. run project:
    - run command `touch setup.py` and then `make venv`  (this will create a virtualenv inside the project).
    - run command `make setup` (this will install all the requirements from requirements.txt)
    - run command  `make run` (this will makemigrations and migrate into database(needs to be looked into) and run the app on port 8000)

`make install` to install all packages
