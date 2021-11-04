import yaml

from functools import reduce

with open('config.yaml', 'r') as f:
    loaded = yaml.load(f.read(), Loader=yaml.FullLoader)
    locals().update(loaded)


def GetValue(keys, default):
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), config)