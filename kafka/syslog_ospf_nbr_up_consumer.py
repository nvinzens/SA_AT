from kafka import KafkaConsumer
from helpers import salt_event
import json

def __get_interface_status(yang_message):
    for k, v in sorted(yang_message.items()):
        if k == 'oper_status':
            return v
        if v:
            return __get_interface_status(v)
        else:
            return ''

consumer = KafkaConsumer('OSPF_NEIGHBOR_UP')

for msg in consumer:
    event_msg = json.loads(msg.value)
    print (event_msg)
    yang_mess = event_msg['yang_message']
    host = event_msg['host']
    ip = event_msg['ip']
    event_tag = event_msg['message_details']['tag']
    message = event_msg['message_details']
    event_error = event_msg['error']
    opt_arg = 'ospf_nbr_up'
    salt_event.send_salt_event(data=yang_mess, host=host, origin_ip=ip, tag=event_tag,
                               message_details=message, error=event_error, opt_arg=opt_arg)




