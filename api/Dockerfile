FROM python:slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR api
COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8800", "--reload"]


