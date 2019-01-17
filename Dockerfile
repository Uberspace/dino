FROM python:3.7

VOLUME /app
COPY . /app
WORKDIR /app/src

RUN pip install -e .

EXPOSE 8001

CMD python manage.py runserver 0.0.0.0:8080
