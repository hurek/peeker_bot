from pony.orm import *
from datetime import *


db = Database('sqlite', 'test.sqlite', create_db=True)


class CreatedEventTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class RedeemedEventTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class FundedEventTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class SetupFailedTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class LiquidatedTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class StartedLiquidationTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class RedemptionRequestedTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class GotRedemptionSignatureTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class PubkeyRegisteredTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class CourtesyCalledTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class RedemptionFeeIncreasedTiming(db.Entity):
    alerts = Required(int, default=int(datetime.timestamp(datetime.now())), unique=True)


class User(db.Entity):
    telegram_id = Required(int, size=64, unique=True, index=True)
    username = Optional(str)

    trackings = Set("Tracking")
    labels = Set("Label")


class Label(db.Entity):
    address = Required("Address")
    user = Required("User")
    label = Optional(str)


class Address(db.Entity):
    operator = Required(str, unique=True, index=True)
    trackings = Set("Tracking")
    labels = Set("Label")


class Tracking(db.Entity):
    operator = Required("Address")
    user = Required("User")
    type = Required(int)