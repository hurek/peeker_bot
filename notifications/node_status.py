"""Here is the logic of node status tracking."""
import jsonpickle
import requests
import json
from pony.orm import *
from configs.db_tools import *
from notifications.event_types import EventTypes


def get_diagnostics_data():
    """A function for sending requests to the diagnostic addresses of running nodes and getting a list of
    dictionaries that contain connected peers, and also the number of sources - the total number of diagnostic
    addresses."""
    with open("notifications/diagnostics.json", 'r') as json_file:
        diagnostic_sources = json.load(json_file)
    diagnostics = []
    sources_total = 0
    for source in diagnostic_sources:
        response = requests.get(source['ecdsa'])  # TODO Handle errors
        diagnostics.append(jsonpickle.decode(response.text))
        sources_total += 1
    return diagnostics, sources_total


def connected_to_peers(address, peer_lists, is_client=False):
    """Here is the logic of determining whether a node is online or disconnected from the network. So far,
    this is a controversial algorithm and it is in beta testing, but we discussed with @Nik G and @Piotr that nodes
    can have different numbers of peers. This can be affected by various factors, for example, the new node did not
    have time to connect to all the peers. therefore, i assume the following: if i meet an address among clients or a
    list of peers in more than 80% of cases-then it is online, otherwise-some network problems or the node is
    disconnected."""
    total_diagnostic_nodes = len(peer_lists)
    total_matches = 1 if is_client is True else 0
    for lst in peer_lists:
        for i in lst:
            if address == i["ethereum_address"].lower():
                total_matches += 1
    if total_matches / total_diagnostic_nodes > 2:
        return True
    return False


@db_session
def check_status(context):
    """Function for managing node status queries and notifications."""
    diagnostics, sources_total = get_diagnostics_data()
    addresses = select(p for p in Address)
    all_clients = [param["client_info"]["ethereum_address"].lower() for param in diagnostics]
    peer_lists = [param["connected_peers"] for param in diagnostics]
    msg = "🆘<b>The node is disconnected!</b>🆘\nI didn't find your node {} among the list of connected peers. Most likely," \
          " your node is disconnected from the network - take measures to fix the problem.\n\n<i>This feature is " \
          "currently in beta testing, so if there was a false notification trigger - please send your feedback.</i>\n" \
          "#disconnected"
    operator_link = "<a href=\"https://allthekeeps.com/operator/{}\">{}</a>"
    for i in addresses:
        users = select(u for u in User if
                       (t.operator.operator == i.operator and t.type == EventTypes.NODESTATUS.value for t in
                        u.trackings))
        operator = Address.get(operator=i.operator)
        if i.operator not in all_clients:
            if not connected_to_peers(i.operator, peer_lists):
                for u in users:
                    label = Label.get(user=u, address=operator)
                    operator_link = operator_link.format(i.operator, label.label)
                    context.bot.send_message(chat_id=u.telegram_id, text=msg.format(operator_link), parse_mode='HTML')
            else:
                continue
        else:
            if not connected_to_peers(i.operator, peer_lists, is_client=True):  # TODO May be remove this double verification?
                for u in users:
                    label = Label.get(user=u, address=operator)
                    operator_link = operator_link.format(i.operator, label.label)
                    context.bot.send_message(chat_id=u.telegram_id, text=msg.format(operator_link), parse_mode='HTML')
