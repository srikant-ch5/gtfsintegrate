#!/bin/sh
sudo -u postgres psql <<EOF
CREATE USER "www-data";
CREATE DATABASE gtfsintegrate_$USER owner "www-data";
\c gtfsintegrate_$USER
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q
EOF