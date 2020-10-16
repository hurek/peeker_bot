from pony.orm import *
from datetime import *

db = Database('sqlite', 'test.sqlite', create_db=True)


class ScheduleTiming(db.Entity):
    alerts = Required(datetime, default=datetime.now(), unique=True)
    stats_time = Required(datetime, unique=True)


class User(db.Entity):
    telegram_id = Required(int, size=64, unique=True)
    username = Optional(str, unique=True)
    addresses = Set('Address')


class Address(db.Entity):
    address_id = Required(str, unique=True)
    address_name = Required(str)
    users = Set('User', reverse='addresses')
    events = Set('Events', reverse='e_addresses')


class Events(db.Entity):
    event_id = Required(int, size=64, unique=True)
    event_name = Optional(str, unique=True)
    e_addresses = Set('Address')
