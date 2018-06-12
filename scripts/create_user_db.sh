#!/bin/sh
sudo -u postgres psql <<EOF
create database $1_gtfsintegrate owner $1;
\c $1_gtfsintegrate
create extension postgis;
create extension postgis_topology;
\q
EOF