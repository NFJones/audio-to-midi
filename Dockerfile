FROM python:3.7

WORKDIR /audio-to-midi
COPY . ./

RUN apt-get update && apt-get install -y libsndfile1
RUN pip install -r requirements.txt
RUN python3 ./setup.py install

VOLUME /src_file

ENTRYPOINT ["audio-to-midi"]
