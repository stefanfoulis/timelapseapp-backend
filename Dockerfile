FROM stefanfoulis/timelapse-manager:base-py3-1.0

#RUN npm install -g npm-install-retry
COPY package.json /package.json
RUN (cd / && npm install)
##RUN (ln -s /app/package.json /package.json && cd / && npm-install-retry)
#RUN (ln -s /app/package.json /package.json && cd / && npm install)

# add full sourcecode
# -------------------
COPY . /app

# static compilation with gulp (e.g sass)
# ---------------------------------------
#ENV GULP_MODE=production
#RUN gulp build; exit 0

# collectstatic
# -------------
RUN DJANGO_MODE=build python manage.py collectstatic --noinput --link
