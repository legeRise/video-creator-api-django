venvname="env92"

if [ ! -d "$venvname" ]; then
    python -m venv "$venvname"
    pip install -r requirements.txt
fi

source "$venvname/bin/activate"
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:9200
