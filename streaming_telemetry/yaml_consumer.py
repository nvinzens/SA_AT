import yaml
import time
from SubscriptionConfig import SubscriptionConfig

config = SubscriptionConfig('config.yaml')
host_configs = config.get_host_configs()
for host_config in host_configs:
    print (config.get_username(host_config))
    print (config.get_password(host_config))
    print (config.get_host(host_config))
    for sub in config.get_subscriptions(host_config):
        print (sub['subscription'])
        print (config.get_xpath(sub))
        print (config.get_kafka_topic(sub))
        print (config.get_publish_period(sub))
    print ("")




#config = open('config.yaml', 'r')
#obj = yaml.load(config)
#hosts = []
#for host in obj['hosts']:
    #print (host)
#    for sub in host['subscriptions']:
#        print sub['subscription']
#    print ("")