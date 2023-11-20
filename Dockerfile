FROM python:3.8
#RUN pip install --upgrade pip
RUN pip install --root-user-action=ignore requests
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "collab.py"]
