FROM python:3.12
ENV TZ="Asia/Shanghai"
WORKDIR /code

COPY ./ /code/
# replace mirror of apt
COPY ./sources/sources.list /etc/apt/ 
# install font
COPY ./sources/arial.ttf /usr/local/share/fonts

RUN pip install -r /code/requirements.txt
RUN apt-get update -y && apt-get install -y chromium
# CHROMIUM default flags for container environnement
# The --no-sandbox flag is needed by default since we execute chromium in a root environnement
RUN echo 'export CHROMIUM_FLAGS="$CHROMIUM_FLAGS --no-sandbox"' >> /etc/chromium.d/default-flags

CMD [ "python", "/code/getInfo.py" ]