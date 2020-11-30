#FROM python:3.5-alpine
#WORKDIR /SpotifyDataExtractor
#ADD . /SpotifyDataExtractor
#RUN apk add --update curl gcc g++ \
#    && rm -rf /var/cache/apk/*
#RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
#RUN pip install bottle numpy cython pandas
#RUN pip install -r requirements.txt
#CMD ["python","app.py"]
FROM python:3
WORKDIR /SpotifyDataExtractor
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "app.py" ]