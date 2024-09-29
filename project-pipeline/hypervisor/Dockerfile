FROM python:3.9-slim
EXPOSE 8081/tcp
ENV SOCKETPORT=8081
COPY . .

RUN pip install -r requirements.txt
CMD [ "python", "-u","./hypervisor.py" ]
