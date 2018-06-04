# Author: Kobe Hu
# Created for SCCR, 2018

# Simple shell script to clear the Django cache (static files) and run the server
# Please note this should only be a temporary fix

cd ..
python3 manage.py collectstatic --noinput --clear
python3 manage.py runserver
