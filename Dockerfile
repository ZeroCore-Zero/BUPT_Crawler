FROM python:3.12
ENV TZ="Asia/Shanghai"
WORKDIR /code

COPY ./ /code/

RUN pip install -r /code/requirements.txt
CMD [ "python", "/code/getInfo.py" ]