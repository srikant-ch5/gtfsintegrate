#!/bin/bash

if [ $# -ne 2 ]
  then
    echo "No arguments supplied"
    echo "Please provide the name for the database and a password"
    echo "a user role will be created automatically"
    echo "with the same name followed by user"
    exit;
fi

echo $1

if [ -z $1 ]
  then
    echo "Please provide the name for the database,"
    exit;
  else
    dbname=$1
fi

dbuser=${dbname}user

if [ -z $2 ]
  then
    echo "Please provide a password for the $dbuser user"
    exit;
  else
    password=$2
fi

sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS $dbname;
DROP USER IF EXISTS $dbuser;
CREATE USER $dbuser WITH PASSWORD '$password';
CREATE DATABASE $dbname OWNER $dbuser;
\c postgres
CREATE EXTENSION IF NOT EXISTS adminpack;
\c $dbname
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
\q
EOF

echo "Please add the following lines to geodjango/settings_secret.py:"
echo "        'NAME': '$dbname',"
echo "        'USER': '$dbuser',"
echo "        'PASSWORD': 'tttttt',"
