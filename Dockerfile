FROM python:3.11.4-slim-bookworm
RUN apt-get update && apt-get upgrade && apt-get install ffmpeg -y && apt-get clean
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT ["python"]
CMD ["main.py"]