from gql import gql, Client, AIOHTTPTransport
import json


# gql settings
transport = AIOHTTPTransport(url='https://api.thegraph.com/subgraphs/name/miracle2k/all-the-keeps')
client = Client(transport=transport, fetch_schema_from_transport=True)


#
def created_events_query(timestamp):
    """Send node stats when the command /stats is issued."""
    query = gql(
        """
		query GetLatestCreatedEvents($timestamp:  BigInt!) {
    createdEvents(where:{timestamp_gt: $timestamp}) {
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
    )
    params = {
        "timestamp": timestamp,
    }
    result = client.execute(query, variable_values=params)
    return json.dumps(result, indent=4)


# createdEvents parser
def created_events_parser(blockchain_data):
    result = []
    try:
        events = blockchain_data['createdEvents']
        for event in events:
            deposit = event['deposit']
            event_data = {
                'link': 'https://allthekeeps.com/deposit/' + str(deposit['id']),
                'members': []
            }
            members = deposit['bondedECDSAKeep']['members']
            for member in members:
                event_data['members'].append(member['address'])
            result.append(event_data)
        print(result)
        return result
    except:
        print('ERROR?')  # TODO how to handle error?
        return