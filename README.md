# gtfsintegrate
Main repository
Install GDAL:  https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/geolibs/#gdal
Install GEOS: https://docs.djangoproject.com/en/2.0/ref/contrib/gis/install/geolibs/#geos

clone the project from https://github.com/sriks123/gtfsintegrate.
Run 'cd gtfsintegrate'.

Install virtualenv and postgres,postgis

A)
'''sudo apt-get install virtualenv python3-dev postgresql-9.6.8 postgresql-9.6.8-postgis-2.1 postgresql-contrib-9.6.8 libpq-dev libgeos-dev redis-server libffi6 libffi-dev'''

To setup database 

B) scripts/create_user_db.sh

If to specify a string as user 

B) 'USER=username scripts/create_user_db.sh'

C) Run the project
Steps to run project through makefile 
1. Run command 'touch setup.py' and then 'make venv'  (this will create a virtualenv inside the project).
2. Run command 'make setup' (this will install all the requirements from requirements.txt) 
3. Run command  'make run' (this will makemigrations and migrate into database(needs to be looked into) and run the app on port 8000)
