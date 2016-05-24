FROM python:2.7

MAINTAINER Daniel Johansson <donnex@donnex.net>

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY feedfetcher.py /app
COPY rssfeed.py /app
COPY settings.py /app

RUN useradd -s /bin/bash -u 3000 -M python_user

USER python_user

CMD ["python", "feedfetcher.py"]
