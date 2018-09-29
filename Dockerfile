FROM stefanfoulis/python:3.7-stretch-v1.4

COPY stack/timelapse /stack/timelapse
RUN /stack/timelapse/install.sh

RUN pipsi install --python=python3 black
RUN pipsi install --python=python3 isort
RUN pipsi install --python=python3 poetry
RUN poetry completions bash > /etc/bash_completion.d/poetry.bash-completion

ENV PATH=/root/.cache/pypoetry/virtualenvs/timelapseapp-backend-py3.7/bin:$PATH \
    DJANGO_SETTINGS_MODULE=settings

COPY addons-dev /app/addons-dev/
COPY pyproject.* /app/
RUN poetry install --no-interaction

# FIXME: install packages

# <SOURCE>
COPY . /app
# </SOURCE>

# <STATIC active=no>
# RUN DJANGO_MODE=build python manage.py collectstatic --noinput
# </STATIC>

# gzip does not seem to work with python3 yet
ENV DISABLE_GZIP=True
