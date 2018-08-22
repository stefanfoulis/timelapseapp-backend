FROM stefanfoulis/python:3.6-stretch-v1.2

COPY stack/timelapse /stack/timelapse
RUN /stack/timelapse/install.sh

RUN pipsi install --python=python3 black
RUN pipsi install --python=python3 isort

#ENV PYTHONPATH=/app/src:/app:$PYTHONPATH

#ENV WORKON_HOME=/virtualenvs

COPY Pipfile* /app/
COPY addons-dev /app/addons-dev/
RUN set -ex && pipenv install --deploy

# <SOURCE>
COPY . /app
# </SOURCE>

# <STATIC active=no>
# RUN DJANGO_MODE=build python manage.py collectstatic --noinput
# </STATIC>

# gzip does not seem to work with python3 yet
ENV DISABLE_GZIP=True
