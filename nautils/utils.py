import hashlib

from nautils.config import Getcfgvalue


def get_level(guild, user):
    user_level = 0

    member = guild.get_member(user)
    levels = Getcfgvalue("options.levels", [])

    if not member:
        return user_level

    for oid in member.roles:
        if oid in levels and levels[oid] > user_level:
            user_level = levels[oid]

    if member.id in levels:
        user_level = levels[member.id]

    return user_level


def parse_natural(timedelta):
    td = timedelta
    if hasattr(td, 'days'):
        years = int(td.days / 365)
        if td.days > 365:
            days = int(td.days) - (years * 365)
        else:
            days = int(td.days)
    hours = int(td.seconds / 3600)
    minutes = int((td.seconds % 3600) / 60)
    if td.total_seconds() > 60:
        value = '{}'.format('{}'.format(str(years) + 'y:' if years else '') + '{}'.format(
            str(days) + 'd:' if td.days else '') + '{}'.format(
            str(hours) + 'h:' if hours else '') + '{}'.format(str(minutes) + 'm' if minutes else '0m'))
    else:
        value = str(int(td.seconds)) + 's'
    return value


def Get_Hash(file):
    fhash = hashlib.md5()
    with open(file, "r", encoding='utf-8') as f:
        while chunk := f.read(8192):
            fhash.update(chunk)
    return fhash.hexdigest()
