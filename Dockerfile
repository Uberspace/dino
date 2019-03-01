FROM python:3.7

EXPOSE 8080
WORKDIR /app

# TODO: do this last
COPY src .
RUN pip install -e . uwsgi

USER 1000
CMD uwsgi --http-socket :8080 --master --workers 8 --module dino.wsgi
