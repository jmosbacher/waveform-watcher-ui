FROM heroku/heroku:18-build

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
# Python, don't write bytecode!
ENV PYTHONDONTWRITEBYTECODE 1

# -- Install Pipenv:
RUN apt update && apt install python3.7-dev libffi-dev -y
RUN curl --silent https://bootstrap.pypa.io/get-pip.py | python3.7

# Backwards compatility.
RUN rm -fr /usr/bin/python3 && ln /usr/bin/python3.7 /usr/bin/python3

RUN pip3 install pipenv


# Requirements are installed here to ensure they will be cached.
COPY ./waveforms/requirements.txt /requirements.txt
RUN pip3 install scikit-build
RUN pip3 install blosc
RUN pip3 install -r /requirements.txt

COPY ./waveforms /app
COPY ./compose/production/waveforms/start /app/start
WORKDIR /app
RUN chmod +x start
CMD panel serve waveforms.py --address 0.0.0.0\
 --port 5006 --allow-websocket-origin='*' --use-xheaders --log-level debug
