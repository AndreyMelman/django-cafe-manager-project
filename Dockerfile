FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./pytest.ini /code/pytest.ini

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./cafe_manager /code/cafe_manager

WORKDIR /code/cafe_manager