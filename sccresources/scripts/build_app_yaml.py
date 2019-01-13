import random
import string
import sys
from pathlib import Path
from ruamel.yaml import YAML

# This script builds the app.yaml used for deployment
# Don't run it manually, let it be called from the makefile

OUT_FILE = 'app.yaml'


def main(argv):
    app_yaml = Path(OUT_FILE)
    if app_yaml.is_file():
        raise ValueError('app.yaml already exists.')

    try:
        maps_key = argv[1]
    except IndexError:
        raise ValueError('maps_key was not set when running `make deploy')

    yaml = YAML()
    with open('template-app.yaml', 'r') as fh:
        content = yaml.load(fh)

    env_vars = content['env_variables']
    env_vars['GOOGLE_MAPS_KEY'] = maps_key
    env_vars['DEPLOYED'] = True
    env_vars['SECRET_KEY'] = ''.join([random.SystemRandom().choice(
        f"{string.ascii_letters}{string.digits}{string.punctuation}") for _ in range(50)])

    with open(OUT_FILE, 'w') as fh:
        yaml.dump(content, fh)


if __name__ == '__main__':
    main(sys.argv)
