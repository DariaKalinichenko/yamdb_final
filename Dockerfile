FROM python:latest
RUN mkdir /code
COPY requirements.txt /code
COPY fixtures.json /code
RUN pip install -r /code/requirements.txt
COPY . /code
WORKDIR /code
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000