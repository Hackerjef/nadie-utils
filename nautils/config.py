import yaml

from functools import reduce

with open('config.yaml', 'r') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)


def Getcfgvalue(keys, default):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), config)
