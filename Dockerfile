from python:3.8-slim-buster

RUN pip install cherrypy
RUN pip install pandas
COPY myprocessor.py .
COPY webservice.py .
EXPOSE 8080

ENTRYPOINT ["python", "webservice.py"]