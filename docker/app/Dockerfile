FROM sample-base:latest

LABEL maintainer="nicc777@gmail.com"
LABEL Description="A container for the production hosting of a flask-restful application" Vendor="none" Version="1.0.0"

# Install the app
WORKDIR /usr/src/app
RUN mkdir dist
COPY *.tar.gz ./dist/
RUN pip3 install dist/*.tar.gz

# Operational Configuration
EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--access-logfile", "-", "sample.simple:app"]
