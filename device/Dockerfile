FROM python:3.9-slim
#FROM python:3.9-alpine
COPY . .
RUN pip3 install -r requirements.txt
#CMD ["python3","./aircon.py","./attract.py","./door.py","./humi.py","./kitchen.py","./light.py","./temp.py","./toilet.py"]
CMD ["python3","./temp.py"]