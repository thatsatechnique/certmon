FROM python:3

LABEL maintainer="28403172+thatsatechnique@users.noreply.github.com"
LABEL version="2.0"

RUN mkdir -p /opt/certmon
COPY . /opt/certmon
WORKDIR /opt/certmon
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["run.py"]
