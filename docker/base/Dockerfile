FROM ubuntu:18.04

LABEL maintainer="nicc777@gmail.com"
LABEL Description="A container for hosting of a flask-restful application" Vendor="none" Version="0.1"

# Prep Python
RUN apt-get update && apt-get upgrade -y
RUN apt-get install libterm-readline-perl-perl apt-utils -y
RUN apt-get install -y python3 python3-pip
RUN pip3 install Flask gunicorn connexion[swagger-ui] psycopg2-binary sqlalchemy
