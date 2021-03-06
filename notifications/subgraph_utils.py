"""Here you can find auxiliary functions for adding operator dialogs and collecting statistics for the operator."""
from gql import gql, Client, AIOHTTPTransport
import json
import locale

# gql settings
transport = AIOHTTPTransport(url='https://api.thegraph.com/subgraphs/name/miracle2k/all-the-keeps')
client = Client(transport=transport, fetch_schema_from_transport=True)


def node_stats(operator_id):
    """Function for querying subgraph for operator's stats."""
    query = gql(
        """
        query GetOperators($id: ID!) {
            operators(where: {id: $id}) {
                address
                bonded
                unboundAvailable
                stakedAmount
                totalFaultCount
                attributableFaultCount
                totalBeaconRewards
                totalETHRewards
                totalTBTCRewards
                activeKeepCount
                totalKeepCount
            }
        }
        """
    )
    params = {
        "id": operator_id,
    }
    result = client.execute(query, variable_values=params)
    return json.dumps(result, indent=4)


def satoshi_to_tbtc(tbtc):
    """Function for converting satoshis to tBTC"""
    return round(tbtc * 0.000000000000000001, 5)


def check_operator(operator_id):
    """Function for querying an operator on a subgraph by its ID. If operator_id not in result, then this ETH address
    not an operator. """
    query = gql(
        """
        query GetOperators($id: ID!) {
            operators(where: {id: $id}) {
                address
                stakedAmount
            }
        }
        """
    )
    params = {
        "id": operator_id,
    }
    result = client.execute(query, variable_values=params)
    if not result['operators']:
        return None
    else:
        return 'ok'


def node_stats_parser(result):
    """Function for parsing result of node_stats function and sending structured messages with stats."""
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
    msg = ""
    bonded = "▫️Bonded: "
    available_to_bond = "▫️Available to bond: "
    staked = "▫️Staked amount: "
    faults = "▫️Faults: "
    tbtc_rewards = "▫️TBTC rewards: "
    try:
        stats = result['operators'][0]
        msg += bonded + '<b>' + str(round(float(stats['bonded']), 2)) + ' ETH' + '</b>' + '\n'
        msg += available_to_bond + '<b>' + str(round(float(stats['unboundAvailable']), 2)) + ' ETH' + '</b>' + '\n'
        msg += staked + '<b>' + locale.format_string("%d", int(stats['stakedAmount']), grouping=True) + ' KEEP' + '</b>' + '\n'
        msg += faults + '<b>' + str(stats['totalFaultCount']) + '</b>' + '\n'
        msg += tbtc_rewards + '<b>' + str(satoshi_to_tbtc(int(stats['totalTBTCRewards']))) + ' TBTC' + '</b>' + '\n'
        return msg
    except:
        return None
