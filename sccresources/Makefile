
# colors for pretty error printing

green=\033[0;32m
normal=\033[0m
red=\033[0;31m
cyan=\033[0;36m


check_venv:
	@python -c 'import sys, os; sys.exit( int( 0 if "VIRTUAL_ENV" \
	in os.environ else 1 ) )' || ( printf "$(red)A virtualenv must be \
	active.$(normal)\n" ; false )

test: check_venv
	mypy .
	flake8 .
	python manage.py test -v 2


# this target builds the app.yaml and does initial configuration for a
# deployment. Make sure

app.yaml: check_venv
# list credentials for logging purposes
	gcloud config list
# the bucket made here will contain the static files used in the
# deployment. If the bucket name is already taken, then choose
# another and note this for your deployment
	@printf "$(cyan)Creating Google Bucket named $(project)$(normal)\n"
	gsutil mb gs://$(project)
	@printf "$(cyan)Making gs://$(project) public$(normal)\n"
	gsutil defacl set public-read gs://$(project)
	@printf "$(green)Creating app.yaml$(normal)\n"
	python scripts/build_app_yaml.py $(project) $(maps_key)


# the deploy target should only be run after init-deploy has been run

deploy: app.yaml check_venv
# list credentials for logging purposes
	gcloud config list
# this variable
	yes yes | python manage.py collectstatic
	@printf "$(cyan)Uploading static files to gs://$(project)$(normal)\n"
#gsutil -m rsync -r static/ gs://$(project)/static
#gcloud app deploy
	@printf "$(green)App successfully deployed!$(normal)\n"

.PHONY: test deploy check_venv