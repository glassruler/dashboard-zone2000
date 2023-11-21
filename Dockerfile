# FROM python:3.8
# RUN pip install --upgrade pip
# RUN pip install --root-user-action=ignore requests
# WORKDIR /app
# COPY . /app
# RUN pip install -r requirements.txt
# CMD ["python", "collab.py"]


FROM python:3.9.3
RUN pip install --upgrade pip

RUN apt-get install -y python3 python3-pip python3-venv
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

CMD ["python3", "collab.py"]
