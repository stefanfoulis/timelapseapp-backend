FROM readthedocs/build:latest
RUN virtualenv --python=python3 /home/docs/virtualenv
ENV PATH=/home/docs/virtualenv/bin:$PATH
COPY requirements.txt /home/docs/docs/
RUN pip install -r /home/docs/docs/requirements.txt
WORKDIR /home/docs/docs
COPY . /home/docs/docs
CMD bash
