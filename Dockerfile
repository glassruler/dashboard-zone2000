FROM python:3.8
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
ENV PIP_ROOT_USER_ACTION=ignore
CMD ["python", "collab.py"]
