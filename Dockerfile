FROM python:3.7

WORKDIR /mimicio
ADD requirements.txt /mimicio/requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg libsndfile1
RUN pip3 install torch==1.4.0+cpu torchvision==0.5.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

ADD . /mimicio

#EXPOSE 5000
ENTRYPOINT ["python3", "run.py"]