FROM python:3.10.4
EXPOSE 8060
WORKDIR /app
COPY app.py /app
COPY requirements.txt /app/requirements.txt
COPY payment_db.py /app
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]