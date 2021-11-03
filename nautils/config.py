import yaml

with open('config.yaml', 'r') as f:
    loaded = yaml.load(f.read(), Loader=yaml.FullLoader)
    locals().update(loaded)
