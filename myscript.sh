venvname="env92"

if [ ! -d "$venvname" ]; then
    python -m venv "$venvname"
    pip install -r requirements.txt
fi

source "$venvname/bin/activate"
python manage.py makemigrations
python manage.py migrate
gunicorn -w 4 -b 0.0.0.0:9200 --reload myproj.wsgi:application
