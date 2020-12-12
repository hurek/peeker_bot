from pycoingecko import CoinGeckoAPI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from notifications.types import *
from notifications.subgraph_utils import *
import jsonpickle
import json
from db_tools import *

event_queries = {
    EventTypes.CREATEDEVENT: 'createdEvents',
    EventTypes.REDEEMEDEVENT: 'redeemedEvents',
    EventTypes.FUNDEDEVENT: 'fundedEvents',
    EventTypes.SETUPFAILED: 'setupFailedEvents',
    EventTypes.LIQUIDATED: 'liquidatedEvents',
    EventTypes.STARTEDLIQUIDATION: 'startedLiquidationEvents',
    EventTypes.REDEMPTIONREQUESTED: 'redemptionRequestedEvents',
    EventTypes.GOTREDEMPTIONSIGNATURE: 'gotRedemptionSignatureEvents',
    EventTypes.PUBKEYREGISTERED: 'registeredPubKeyEvents',
    EventTypes.COURTESYCALLED: 'courtesyCalledEvents',
    EventTypes.REDEMPTIONFEEINCREASED: 'redemptionFeeIncreasedEvents'
}

entities = {
        EventTypes.CREATEDEVENT: CreatedEventTiming,
        EventTypes.REDEEMEDEVENT: RedeemedEventTiming,
        EventTypes.FUNDEDEVENT: FundedEventTiming,
        EventTypes.SETUPFAILED: SetupFailedTiming,
        EventTypes.LIQUIDATED: LiquidatedTiming,
        EventTypes.STARTEDLIQUIDATION: StartedLiquidationTiming,
        EventTypes.REDEMPTIONREQUESTED: RedemptionRequestedTiming,
        EventTypes.GOTREDEMPTIONSIGNATURE: GotRedemptionSignatureTiming,
        EventTypes.PUBKEYREGISTERED: PubkeyRegisteredTiming,
        EventTypes.COURTESYCALLED: CourtesyCalledTiming,
        EventTypes.REDEMPTIONFEEINCREASED: RedemptionFeeIncreasedTiming,
}

replace_dict = {
        EventTypes.CREATEDEVENT: 'deposit',
        EventTypes.REDEEMEDEVENT: 'deposits',
        EventTypes.FUNDEDEVENT: 'deposits',
        EventTypes.SETUPFAILED: 'deposits',
        EventTypes.LIQUIDATED: 'deposits',
        EventTypes.STARTEDLIQUIDATION: 'Liquidation',
        EventTypes.REDEMPTIONREQUESTED: 'Redemption',
        EventTypes.GOTREDEMPTIONSIGNATURE: 'Redemption Signature',
        EventTypes.PUBKEYREGISTERED: 'registered',
        EventTypes.COURTESYCALLED: 'created',
        EventTypes.REDEMPTIONFEEINCREASED: 'increased',
        EventTypes.CRATIODECREASED: 'has fallen below 130%'
}


def return_msg(event_type, link, label, address, cratio=None):
    operator_link = f'''<a href="https://allthekeeps.com/operator/{address}">{label}</a>'''
    event_link = f'''<a href="{link}">{replace_dict[event_type]}</a>'''
    message_samples = {
        EventTypes.CREATEDEVENT: f'''🔸New Deposit🔸\nYour operator {operator_link} got selected for a new {event_link}.\n\n#created #{label.replace(' ', '_')}''',
        EventTypes.REDEEMEDEVENT: f'''🔹Deposit Redeemed🔹\nOne of the {event_link} of your operator {operator_link} was redeemed.\n\n#redeemed #{label.replace(' ', '_')}''',
        EventTypes.FUNDEDEVENT: f'''🔸Deposit Funded🔸\nOne of the {event_link} of your operator {operator_link} has been funded.\n\n#funded #{label.replace(' ', '_')}''',
        EventTypes.SETUPFAILED: f'''🔻Setup Failed🔻\nOne of the {event_link} of your operator {operator_link} was failed to setup.\n\n#setup_failed #{label.replace(' ', '_')}''',
        EventTypes.LIQUIDATED: f'''🔻Deposit Liquidated🔻\nOne of the {event_link} of your operator {operator_link} was liquidated.\n\n#liquidated #{label.replace(' ', '_')}''',
        EventTypes.STARTEDLIQUIDATION: f'''🔻Liquidation Started🔻\n{event_link} has been started for one of {operator_link} deposits.\n\n#liquidation_started #{label.replace(' ', '_')}''',
        EventTypes.REDEMPTIONREQUESTED: f'''🔹Redemption Started🔹\n{event_link} has been started for one of {operator_link} deposits.\n\n#redemption_started #{label.replace(' ', '_')}''',
        EventTypes.GOTREDEMPTIONSIGNATURE: f'''🔸Redemption Signature🔸\nYour operator {operator_link} provided {event_link} for one of deposits.\n\n#got_redemption_signature #{label.replace(' ', '_')}''',
        EventTypes.PUBKEYREGISTERED: f'''🔸Public Key Registered🔸\nPublic Key has been {event_link} for one of {operator_link} deposits.\n\n#pubkey_registered #{label.replace(' ', '_')}''',
        EventTypes.COURTESYCALLED: f'''🔻Courtesy Call🔻\nCourtesy Call has been {event_link} for one of {operator_link} deposits.\nYou can click the button to redeem.\n\n#courtesy_call #{label.replace(' ', '_')}''',
        EventTypes.REDEMPTIONFEEINCREASED: f'''🔹Redemption Fee Increased🔹\nRedemption fee has been {event_link} for one of {operator_link} deposits.\n\n#redemption_fee_increased #{label.replace(' ', '_')}''',
        EventTypes.CRATIODECREASED: f'''🔻Collateralization Decreased🔻\nCollateralization {event_link} for one of {operator_link} deposits. Current collateralization ratio: <b>{cratio}%</b>. Be careful!\nYou can click the button to redeem.\n\n#c_ratio_decreased #{label.replace(' ', '_')}'''
    }
    return message_samples[event_type]


def get_time_from_db(event_type):
    if not (date := select(date for date in entities[event_type]).order_by(lambda date: desc(date.id)).first()):
        date = entities[event_type](alerts=int(datetime.timestamp(datetime.now())))
        commit()
    return date.alerts


def put_time_to_db(event_type):
    current = entities[event_type](alerts=int(datetime.timestamp(datetime.now())))
    commit()
    return


def event_query(timestamp, event_type):
    query_pattern = """
		query GetLatestEvents($timestamp:  BigInt!) {""" + \
                    f"""{event_type}""" + \
                    """(where:{timestamp_gt: $timestamp}) {
      id
      timestamp
      deposit {
        id
        bondedECDSAKeep {
          members
          {
            address
          }
        }
      }
    }
}"""
    query = gql(query_pattern)
    params = {
        "timestamp": timestamp,
    }
    result = client.execute(query, variable_values=params)
    return json.dumps(result, indent=4)


def get_active_deposits():
    skip = 0
    query = gql(
        """
        query GetActiveDeposits($skip:  Int!) {
            deposits(first: 1000 skip: $skip where: {currentState: ACTIVE}) {
                id
                lotSizeSatoshis
                bondedECDSAKeep {
                    totalBondAmount
                    members {
                        address
                    }
                }
            }
        }
        """
    )
    params = {"skip": skip}
    result = client.execute(query, variable_values=params)["deposits"]
    deposits = result
    while len(result) == 1000:
        params["skip"] += 1000
        result = client.execute(query, variable_values=params)["deposits"]
        deposits += result
    return deposits


def events_parser(blockchain_data, event_type):
    result = []
    try:
        events = blockchain_data[event_type]
        for event in events:
            deposit = event['deposit']
            event_data = {
                'id': str(deposit['id']),
                'link': 'https://allthekeeps.com/deposit/' + str(deposit['id']),
                'members': []
            }
            members = deposit['bondedECDSAKeep']['members']
            for member in members:
                event_data['members'].append(member['address'])
            result.append(event_data)
        return result
    except:
        # TODO exception handle
        return


@db_session
def event_manager(context):
    job = context.job
    event_type = job.context
    timestamp = get_time_from_db(event_type)
    try:
        blockchain_data = jsonpickle.decode(event_query(timestamp, event_queries[event_type]))
        if not (events_data := events_parser(blockchain_data, event_queries[event_type])):
            return
        put_time_to_db(event_type)
        for event in events_data:
            for address in event['members']:
                users = select(u for u in User if (t.operator.operator == address and t.type == event_type.value for t in u.trackings))
                operator = Address.get(operator=address)
                for i in users:
                    label = Label.get(user=i, address=operator)
                    msg = return_msg(event_type, event['link'], label.label, address)
                    if event_type == EventTypes.COURTESYCALLED:
                        redeem_inline_keyboard = [[InlineKeyboardButton("Redeem", url=f"""https://dapp.tbtc.network/deposit/{event["id"].replace('dp-', '')}/redeem""")]]
                        redeem_inline_kb = InlineKeyboardMarkup(redeem_inline_keyboard)
                        context.bot.send_message(chat_id=i.telegram_id, text=msg, reply_markup=redeem_inline_kb, parse_mode='HTML')
                    else:
                        context.bot.send_message(chat_id=i.telegram_id, text=msg, parse_mode='HTML')
    except:
        return


@db_session
def collateralization(context):
    cg = CoinGeckoAPI()
    eth_btc_price = cg.get_price(ids='ethereum', vs_currencies='btc')["ethereum"]["btc"]
    sat_per_wei = eth_btc_price * 100000000 * 0.000000000000000001
    wei_per_sat = 1 / sat_per_wei
    try:
        if not (deposits := get_active_deposits()):
            return
        for deposit in deposits:
            lotValueWei = int(deposit["lotSizeSatoshis"]) * wei_per_sat
            if (ratio := round(int(deposit["bondedECDSAKeep"]["totalBondAmount"]) / lotValueWei * 100, 2)) < 130:
                operators = deposit["bondedECDSAKeep"]["members"]
                redeem_inline_keyboard = [[InlineKeyboardButton("Redeem", url=f"""https://dapp.tbtc.network/deposit/{deposit["id"].replace('dp-', '')}/redeem""")]]
                redeem_inline_kb = InlineKeyboardMarkup(redeem_inline_keyboard)
                link = 'https://allthekeeps.com/deposit/' + str(deposit['id'])
                for operator in operators:
                    users = select(u for u in User if (t.operator.operator == operator["address"] and t.type == EventTypes.CRATIODECREASED.value for t in u.trackings))
                    operator = Address.get(operator=operator["address"])
                    for i in users:
                        label = Label.get(user=i, address=operator)
                        msg = return_msg(EventTypes.CRATIODECREASED, link, label.label, operator.operator, ratio)
                        context.bot.send_message(chat_id=i.telegram_id, text=msg, reply_markup=redeem_inline_kb, parse_mode='HTML')
    except:
        return