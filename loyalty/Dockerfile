FROM python:3.10.4
EXPOSE 8050
WORKDIR /app
COPY app.py /app
COPY loyalty_db.py /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]