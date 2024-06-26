FROM python:3.9-slim
#FROM python:3.9-alpine
COPY . .
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD ["python3","./telegram.py"]
