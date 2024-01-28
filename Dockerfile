FROM python:3.12

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY app.py ./

ADD app.py .

RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "./app.py"]

COPY ./boot.sh ./boot.sh
RUN chmod +x boot.sh

EXPOSE 80
ENTRYPOINT ["./boot.sh"]
