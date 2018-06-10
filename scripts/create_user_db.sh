#!/bin/sh
sudo -u postgres psql <<EOF
create user "www-data"
create database gtfsintegrate_$USER owner "www-data";
\c gtfsintegrate_$USER
create extension postgis;
create extension postgis_topology;
\q
EOF