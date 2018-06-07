FROM python:3

LABEL maintainer="mkiukaji@gmail.com"
LABEL version="1.0"

RUN mkdir -p /opt/certmon
COPY . /opt/certmon
WORKDIR /opt/certmon
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["run.py"]
