from python:3.8-slim-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y

# update pip
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Install dependencies:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY webservice.py .
COPY openCV_diff_classes.py .

EXPOSE 9191

ENTRYPOINT ["python", "webservice.py"]