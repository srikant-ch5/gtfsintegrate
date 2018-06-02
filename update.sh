#!/bin/bash

#funtion arguments -> filename to compare against curr time
comparedate() {
if [ ! -f "$1" ]; then
  echo "file $1 does not exist"
        exit 1
fi
MAXAGE=$(bc <<< '1*60*60') # seconds in 1 hour
# file age in seconds = current_time - file_modification_time.
FILEAGE=$(($(date +%s) - $(stat -c '%Y' "$1")))
test $FILEAGE -lt $MAXAGE && {
    echo "$1 is less than 1 hour old."
    return 0
}
echo "$1 is older than 1 hour."
return 1
}

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Repositories are up-to-date"
elif [ $LOCAL = $BASE ]; then
    # pull latest version from github if there is one, abort when that fails
    git pull || { echo 'pulling from github failed' ; exit 1; }
elif [ $REMOTE = $BASE ]; then
    git push
    exit 1;
else
    echo "Repositories diverged"
    exit 1;
fi
git pull || { echo 'pulling from github failed' ; exit 1; }
# only pip install from requirements.txt, when file was modified in last hour
requirements=requirements.txt
if comparedate $requirements;
then
    pip install -r $requirements
fi
fetched=".git/index"
if comparedate $fetched;
then
    python manage.py makemigrations --merge
    python manage.py makemigrations
    python manage.py migrate
    touch ~/www/mysite.fcgi
fi
