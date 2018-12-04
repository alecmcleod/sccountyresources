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
        project = argv[1]
        maps_key = argv[2]
    except IndexError:
        raise ValueError('project and/or maps_key were not set when running `make deploy')

    yaml = YAML()
    with open('template-app.yaml', 'r') as fh:
        content = yaml.load(fh)

    env_vars = content['env_variables']
    env_vars['PROJECT_NAME'] = project
    env_vars['GOOGLE_MAPS_KEY'] = maps_key
    env_vars['DEPLOYED'] = True

    with open(OUT_FILE, 'w') as fh:
        yaml.dump(content, fh)


if __name__ == '__main__':
    main(sys.argv)
