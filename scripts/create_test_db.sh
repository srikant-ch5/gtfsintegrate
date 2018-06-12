#!/bin/sh
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS $1_gtfsintegrate_test;
DROP USER IF EXISTS $1;
CREATE USER $1 WITH PASSWORD 'password';
CREATE DATABASE $1_gtfsintegrate_test OWNER $1;
\c postgres
CREATE EXTENSION IF NOT EXISTS adminpack;
\c $1_gtfsintegrate_test
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
\q
EOF
