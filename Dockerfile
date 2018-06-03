#<WARNING>
#</WARNING>
# <DOCKER_FROM>
FROM aldryn/base-project:py3-3.25
# </DOCKER_FROM>

COPY stack/imageopt /stack/imageopt
RUN /stack/imageopt/install.sh

COPY stack/moviepy /stack/moviepy
RUN /stack/moviepy/install.sh

RUN pipsi install --python=python3 pipenv
RUN pipsi install --python=python3 black
RUN pipsi install --python=python3 isort

ENV PYTHONPATH=/app/src:/app:$PYTHONPATH

ENV PIP_INDEX_URL=${PIP_INDEX_URL:-https://wheels.aldryn.net/v1/aldryn-extras+pypi/${WHEELS_PLATFORM:-aldryn-baseproject-py3}/+simple/} \
    WHEELSPROXY_URL=${WHEELSPROXY_URL:-https://wheels.aldryn.net/v1/aldryn-extras+pypi/${WHEELS_PLATFORM:-aldryn-baseproject-py3}/}
ENV WORKON_HOME=/virtualenvs
COPY Pipfile* /app/
COPY addons-dev /app/addons-dev/
RUN set -ex && pipenv install --deploy --system

#COPY requirements.* /app/
#COPY addons-dev /app/addons-dev/
#RUN pip-reqs compile
#RUN pip-reqs resolve && pip install --no-index --no-deps --requirement requirements.urls


# <SOURCE>
COPY . /app
# </SOURCE>

# <STATIC active=no>
# RUN DJANGO_MODE=build python manage.py collectstatic --noinput
# </STATIC>

# gzip does not seem to work with python3 yet
ENV DISABLE_GZIP=True
