FROM python:3.6
ADD . /webping
WORKDIR /webping
RUN pip install -U pip pipenv
RUN pipenv install --system --deploy

RUN python manage.py collectstatic --noinput

EXPOSE 5000

CMD ["gunicorn", "webping.wsgi", "-b:5000", "-w 10"]
