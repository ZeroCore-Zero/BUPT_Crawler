FROM python:3.11
ENV TZ="Asia/Shanghai"
WORKDIR /code

COPY ./ /code/

RUN pip install -r /code/requirements.txt
CMD [ "python", "/code/getInfo.py" ]