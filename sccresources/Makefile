
# colors for pretty error printing

green=\033[0;32m
normal=\033[0m
red=\033[0;31m
cyan=\033[0;36m


check_venv:
	@python -c 'import sys, os; sys.exit( int( 0 if "VIRTUAL_ENV" \
	in os.environ else 1 ) )' || ( printf "$(red)A virtualenv must be \
	active.$(normal)\n" ; false )

check_maps_key:
	test $(maps_key)|| ( printf "$(red)maps_key is not set! run make \
	deploy maps_key=YOUR_MAPS_KEY$(normal)\n"; false)

test: check_venv
	mypy .
	flake8 .
	python manage.py test -v 2


# this target builds the app.yaml and does initial configuration for a
# deployment.
app.yaml: check_venv check_maps_key
	@printf "$(green)Creating app.yaml$(normal)\n"
	python scripts/build_app_yaml.py $(maps_key)

# the redeploy target should only be run after init-deploy has been run
redeploy: check_venv
# list credentials for logging purposes
	gcloud config list
# this variable
	yes yes | python manage.py collectstatic
	yes | gcloud app deploy
	@printf "$(green)App successfully deployed!$(normal)\n"

init-deploy: app.yaml redeploy

.PHONY: test travis-deploy redeploy init-deploy build-static check_venv check_project check_maps_key