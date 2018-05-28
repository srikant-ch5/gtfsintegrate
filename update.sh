git pull || { echo 'pulling from github failed' ; exit 1; }
pip install -r requirements.txt
python manage.py makemigrations --merge
python manage.py makemigrations
python manage.py migrate
touch ~/www/mysite.fcgi
