#!/bin/sh

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Repositories are up-to-date"
elif [ $LOCAL = $BASE ]; then
    git pull || { echo 'pulling from github failed' ; exit 1; }
    pip install -r requirements.txt
    python manage.py makemigrations --merge
    python manage.py makemigrations
    python manage.py migrate
    touch ~/www/mysite.fcgi
elif [ $REMOTE = $BASE ]; then
    git push
else
    echo "Repositories diverged"
fi



