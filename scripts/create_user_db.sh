#!/bin/sh
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS $1_gtfsintegrate;
DROP USER IF EXISTS $1;
CREATE USER $1;
CREATE DATABASE $1_gtfsintegrate owner $1;
\c $1_gtfsintegrate
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q
EOF
