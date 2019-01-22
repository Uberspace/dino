FROM python:3.7

VOLUME /app
COPY src /app
WORKDIR /app

RUN pip install -e .

EXPOSE 8001

CMD python manage.py runserver 0.0.0.0:8000
