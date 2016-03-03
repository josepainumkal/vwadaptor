FROM itsrifat/vw-py:1.0
MAINTAINER Moinul Hossain

LABEL description="This Image builds an ubuntu 14.04 image from vw-py:1.0 and installs the dependencies of vwadaptor." \
      version="1.0"

RUN apt-get update -y
RUN apt-get install -y libpq-dev
#set the env vars

# production or dev?
ENV VWADAPTOR_ENV prod
ENV VWADAPTOR_UPLOAD_FOLDER /vwuploads
ENV VWADAPTOR_SQLALCHEMY_DATABASE_URI postgresql://postgres:postgres@postgres:5432/postgres
ENV VWADAPTOR_CELERY_BROKER_URL redis://redis:6379/0
ENV VWADAPTOR_CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
# copy source code
COPY . /var/www/vwadaptor
WORKDIR /var/www/vwadaptor

# install requirements
RUN pip install -r requirements.txt

# init db
#RUN python manage.py db init
#RUN python manage.py db migrate
#RUN python manage.py db upgrade

# expose the app port
EXPOSE 5000
EXPOSE 5555
EXPOSE 22
# run the app server
ENTRYPOINT ["python"]
CMD ["manage.py","runserver","-h","0.0.0.0"]
