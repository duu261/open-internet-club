FROM python:3.12-slim
WORKDIR /srv/club
COPY . /srv/club
RUN mkdir -p /srv/club/data
EXPOSE 8080
CMD ["python", "server/app.py"]
