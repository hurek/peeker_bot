from pony.orm import *
from datetime import *

db = Database('sqlite', 'test.sqlite', create_db=True)


class ScheduleTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)
    #stats_time = Optional(datetime, unique=True)


class User(db.Entity):
    telegram_id = Required(int, size=64, unique=True)
    username = Optional(str, unique=True)
    addresses = Set('Address')


class Address(db.Entity):
    name = Optional(str)
    operator = Required(str, unique=True)
    users = Set('User', reverse='addresses')
    events = Set('Events', reverse='e_addresses')


class Events(db.Entity):
    event_id = Required(int, size=64, unique=True)
    event_name = Optional(str, unique=True)
    e_addresses = Set('Address')
