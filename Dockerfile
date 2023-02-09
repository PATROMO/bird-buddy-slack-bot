FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pybirdbuddy
RUN pip install --no-cache-dir slack_sdk
RUN pip install --no-cache-dir python-dotenv

COPY . .

CMD [ "python", "./main.py" ]