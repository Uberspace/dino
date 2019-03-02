FROM python:3.7

EXPOSE 8080
WORKDIR /app

# install deps only, for caching
COPY src/setup.py .
RUN pip install -e .

# install dino itself
COPY src .
RUN pip install -e .

USER 1000
CMD uwsgi --http-socket :8080 --master --workers 8 --module dino.wsgi
