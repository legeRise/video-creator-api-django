FROM python:3.8.6-slim AS builder

WORKDIR /djangoApp
COPY requirements.txt .
RUN python -m venv env92 &&  . env92/bin/activate &&  pip install --upgrade pip && pip install -r requirements.txt 
COPY . .
ENV PATH='/djangoApp/env92/bin:$PATH'

RUN python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic


FROM python:3.8.6-slim

WORKDIR /djangoApp
COPY --from=builder /djangoApp/ /djangoApp/
ENV PATH='/djangoApp/env92/bin:$PATH'
EXPOSE 80
CMD ["gunicorn","-w","2","-b","0.0.0.0:80","--timeout","92","myproj.wsgi:application"]






