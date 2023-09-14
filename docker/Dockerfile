FROM openjdk:8-slim

ENV TZ "Asia/Shanghai"

RUN apt update -y \
    && apt install -y software-properties-common \
    && apt install -y git gcc poppler-utils libgl1-mesa-glx libtesseract-dev tesseract-ocr tesseract-ocr-chi-sim ghostscript mupdf mupdf-tools \
    && apt autoclean

RUN add-apt-repository 'ppa:deadsnakes/ppa' \
    && apt install -y python3-pip python3.9 \
    && apt autoclean

RUN pip3 install --upgrade pip -i https://pypi.douban.com/simple

WORKDIR /data/pdf-parser

COPY . .

RUN pip3 install . -i https://pypi.douban.com/simple
