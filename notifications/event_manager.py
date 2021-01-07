"""Here you can find all the logic of requests to the subgraph, parsing responses, searching for event participants
and sending them notificationss."""
from datetime import datetime

from gql_query_builder import GqlQuery
from graphqlclient import GraphQLClient
from pony.orm import select, commit, desc, db_session
from pycoingecko import CoinGeckoAPI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from notifications.event_types import EventTypes
import jsonpickle
from configs.db_tools import Address, Label, LastestCheck, User

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
        EventTypes.CRATIODECREASED: 'has fallen below 135%'
}


def return_msg(event_type, link, label, address, cratio=None, deposit_id=None):
    """Universal function that creates a message for notification. The message contains a link to the operator and a
    link to the deposit on the site allthekeeps.com. """
    operator_link = f'''<a href="https://allthekeeps.com/operator/{address}">{label}</a>'''
    if event_type in [EventTypes.COURTESYCALLED, EventTypes.CRATIODECREASED]:
        event_link = f'''<a href="{link}">{deposit_id.replace('dp-', '')}</a>'''
    else:
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
        EventTypes.COURTESYCALLED: f'''🔻Courtesy Call🔻\nCourtesy Call has been created for deposit {event_link} of your operator {operator_link}.\nYou can click the button to redeem.\n\n#courtesy_call #{label.replace(' ', '_')}''',
        EventTypes.REDEMPTIONFEEINCREASED: f'''🔹Redemption Fee Increased🔹\nRedemption fee has been {event_link} for one of {operator_link} deposits.\n\n#redemption_fee_increased #{label.replace(' ', '_')}''',
        EventTypes.CRATIODECREASED: f'''🔻Collateralization Decreased🔻\nCollateralization has fallen below 135% for deposit {event_link} of your operator {operator_link}.\nCurrent collateralization ratio: <b>{cratio}%</b>. Be careful!\nYou can click the button to redeem.\n\n#c_ratio_decreased #{label.replace(' ', '_')}'''
    }
    return message_samples[event_type]


def get_time_from_db():
    """Universal function for getting the last check timestamp from the database."""
    if not (date := select(date for date in LastestCheck).order_by(lambda date: desc(date.id)).first()):
        date = LastestCheck(timestamp=int(datetime.timestamp(datetime.now())))
        commit()
    return date.timestamp


def put_time_to_db(timestamp):
    """Universal function for putting the current timestamp to the database."""
    current = LastestCheck(timestamp=timestamp)
    commit()
    return


def events_parser(events):
    """Function for parsing result of Events queries."""
    result = []
    try:
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


def event_query(timestamp):
    """Universal function for querying subgraph."""
    graphql_client = GraphQLClient('https://api.thegraph.com/subgraphs/name/miracle2k/all-the-keeps')
    members = GqlQuery().fields(['address']).query('members').generate()
    bondedECDSAKeep = GqlQuery().fields([members]).query('bondedECDSAKeep').generate()
    deposit = GqlQuery().fields(['id', bondedECDSAKeep]).query('deposit').generate()

    queries = []
    for event in event_queries.values():
        queries.append(GqlQuery()
                       .fields(['id', 'timestamp', deposit])
                       .query(event, input={'where': '{timestamp_gt: ' + str(timestamp) + '}'})
                       .generate())
    final_query = GqlQuery().fields(queries).generate()

    result = jsonpickle.decode(graphql_client.execute(final_query))
    final_events = {}
    for event_type, events in result['data'].items():
        if not events:
            continue
        final_events.update({event_type: events_parser(events)})
    return final_events


def get_active_deposits():
    """Function for querying subgraph for all active deposits."""
    skip = 0
    graphql_client = GraphQLClient('https://api.thegraph.com/subgraphs/name/miracle2k/all-the-keeps')
    members = GqlQuery().fields(['address']).query('members').generate()
    bondedECDSAKeep = GqlQuery().fields(['totalBondAmount', members]).query('bondedECDSAKeep').generate()
    deposits_query = GqlQuery().fields(['id', 'lotSizeSatoshis', bondedECDSAKeep]).query('deposits', input={
        "first: 1000 skip: $skip where": "{currentState: ACTIVE}"}).operation('query', name='GetActiveDeposits',
                                                                              input={"$skip": "Int!"}).generate()

    params = {"skip": skip}
    result = jsonpickle.decode(graphql_client.execute(deposits_query, variables=params))["data"]["deposits"]
    deposits = result
    while len(result) == 1000:
        params["skip"] += 1000
        result = jsonpickle.decode(graphql_client.execute(deposits_query, variables=params))["data"]["deposits"]
        deposits += result
    return deposits


@db_session
def event_manager(context):
    """Universal function for managing queries and Event notifications."""
    current_timestamp = int(datetime.timestamp(datetime.now()))
    timestamp = get_time_from_db()
    try:
        if not (events_data := event_query(timestamp)):
            return
        for event_type, query_type in event_queries.items():
            if query_type not in events_data.keys():
                continue
            for event in events_data[query_type]:
                for address in event['members']:
                    users = select(u for u in User if (t.operator.operator == address and t.type == event_type.value for t in u.trackings))
                    operator = Address.get(operator=address)
                    for i in users:
                        label = Label.get(user=i, address=operator)
                        if event_type == EventTypes.COURTESYCALLED:
                            msg = return_msg(event_type, event['link'], label.label, address, deposit_id=event['id'])
                            redeem_inline_keyboard = [[InlineKeyboardButton("Redeem", url=f"""https://dapp.tbtc.network/deposit/{event["id"].replace('dp-', '')}/redeem""")]]
                            redeem_inline_kb = InlineKeyboardMarkup(redeem_inline_keyboard)
                            context.bot.send_message(chat_id=i.telegram_id, text=msg, reply_markup=redeem_inline_kb, parse_mode='HTML')
                        else:
                            msg = return_msg(event_type, event['link'], label.label, address)
                            context.bot.send_message(chat_id=i.telegram_id, text=msg, parse_mode='HTML')
        put_time_to_db(current_timestamp)
    except:
        return


@db_session
def collateralization(context):
    """Function for managing queries and Collateralization notifications."""
    cg = CoinGeckoAPI()
    eth_btc_price = cg.get_price(ids='ethereum', vs_currencies='btc')["ethereum"]["btc"]
    sat_per_wei = eth_btc_price * 100000000 * 0.000000000000000001
    wei_per_sat = 1 / sat_per_wei
    try:
        if not (deposits := get_active_deposits()):
            return
        for deposit in deposits:
            lotValueWei = int(deposit["lotSizeSatoshis"]) * wei_per_sat
            if (ratio := round(int(deposit["bondedECDSAKeep"]["totalBondAmount"]) / lotValueWei * 100, 2)) < 135:
                operators = deposit["bondedECDSAKeep"]["members"]
                redeem_inline_keyboard = [[InlineKeyboardButton("Redeem", url=f"""https://dapp.tbtc.network/deposit/{deposit["id"].replace('dp-', '')}/redeem""")]]
                redeem_inline_kb = InlineKeyboardMarkup(redeem_inline_keyboard)
                link = 'https://allthekeeps.com/deposit/' + str(deposit['id'])
                for operator in operators:
                    users = select(u for u in User if (t.operator.operator == operator["address"] and t.type == EventTypes.CRATIODECREASED.value for t in u.trackings))
                    operator = Address.get(operator=operator["address"])
                    for i in users:
                        label = Label.get(user=i, address=operator)
                        msg = return_msg(EventTypes.CRATIODECREASED, link, label.label, operator.operator, ratio, deposit_id=deposit["id"])
                        context.bot.send_message(chat_id=i.telegram_id, text=msg, reply_markup=redeem_inline_kb, parse_mode='HTML')
    except:
        return