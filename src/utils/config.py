import yaml

def get_config():
    with open("../../conf/default.yaml", 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    return config