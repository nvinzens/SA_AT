from kafka import KafkaConsumer
from kafka import KafkaProducer
from oats_kafka_helpers import EventProcessor
import json
import time

consumer = KafkaConsumer('oats-netflow-ingress')

for msg in consumer:
    netflow_data = json.loads(msg.value)
    host = netflow_data['AgentID']
    timestamp = netflow_data['Header']['UNIXSecs']
    type = 'netflow'
    event_name = 'netflow/*/high_traffic'
    severity = 3

    for list in netflow_data['DataSets']:
        for dict in list:
            if dict['I'] == 1:
                if dict['V'] > 1000:
                    print ("Packets in detected flow: " + str(dict['V']))
                    # delay the flow for a bit to make sure it arrives later than the event it is needed in
                    time.sleep(12)
                    EventProcessor.process_event(data=netflow_data, host=host, timestamp=timestamp, type=type,
                                                 event_name=event_name,
                                                 severity=severity, start_tshoot=True,
                                                 db_write=False)


