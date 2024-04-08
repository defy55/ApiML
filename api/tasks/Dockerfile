FROM python:slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR api
COPY . .

COPY requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip install -r /requirements.txt

#we don't use poetry because watchmedo doesn't work with "poetry run watchmedo"
ENTRYPOINT watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A tasks worker --concurrency=1 --loglevel=INFO
