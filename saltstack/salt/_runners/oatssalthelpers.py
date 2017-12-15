from oats import oatsdbhelpers
import time
import salt.config
import salt.utils.event


# TODO: add behaviour for calling methods without current_case id

def post_slack(message, case=None):
    '''
    Posts a message to the predefined oats slack channel. The message contains the message param
    + all of the involved solution steps for the current case.
    :param message: the message to post to the channel.
    :param case: case-id for updating the current case
    '''
    channel = '#testing'
    user = 'OATS'
    #Use the slack api key for your workspace
    api_key = '12345'
    oatsdbhelpers.update_case(case, solution='Workflow finished. Case-ID: ' + case, status=oatsdbhelpers.Status.ONHOLD.value)
    solutions = oatsdbhelpers.get_solutions_as_string(case)
    message += "\nExecuted workflow:\n" + solutions
    __salt__['salt.cmd'](fun='slack.post_message', channel=channel, message=message, from_name=user, api_key=api_key)


def ping(source, destination, case=None, check_connectivity=False):
    '''
    Executes a ping from one host to another using the salt-api. If check_connectivity is set
    to true it will use the mgmt vrf destination address.
    :param source: The ping source
    :param destination: The ping destination
    :param case: case-id for updating the current case
    :return: The results of the ping as a dict. Will be empty if the ping wasn't successful.
    '''
    if check_connectivity:
        vrf_dest = {'destination': oatsdbhelpers.get_vrf_ip(destination), 'vrf': 'mgmt'}
        ping_result = __salt__['salt.execute'](source, 'net.ping', kwarg=vrf_dest)
        oatsdbhelpers.update_case(case, solution='Ping from ' + source + ' to ' + destination + '. Result: ' + str(
            bool(ping_result)))
        return ping_result[source]['out']['success']['results']
    else:
        ping_result = __salt__['salt.execute'](source, 'net.ping', {destination})
        oatsdbhelpers.update_case(case, solution ='Ping from ' + source + ' to ' + destination + '. Result: ' + str(bool(ping_result)) + ' //always true in lab env')
    return ping_result[source]['out']['success']['results']


def if_noshutdown(host, interface, case=None):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
    '''
    template_name = 'noshutdown_interface'
    template_source = 'interface ' + interface + '\n  no shutdown\nend'
    config = {'template_name': template_name, 'template_source': template_source}
    oatsdbhelpers.update_case(case, solution='Trying to apply no shutdown to interface {0} on host {1}.'.format(interface, host))
    return __salt__['salt.execute'](host, 'net.load_template', kwarg=config)


def if_shutdown(host, interface, case=None):
    '''
    Attempts to load the no shutdown config for the specified interface on the specified host (via napalm).
    Can only be used on ios devices in current state.
    :param host: The target host.
    :param interface: The target interface
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
        '''
    template_name = 'shutdown_interface'
    template_source = 'interface {0}\n  shutdown\nend'.format(interface)
    config = {'template_name': template_name,'template_source': template_source}
    oatsdbhelpers.update_case(case, solution='Trying to apply shutdown to interface {0} on host {1}.'.format(interface, host))
    return __salt__['salt.execute'](host, 'net.load_template', kwarg=config)


def ospf_shutdown(minion, process_number, case=None):
    '''
    Attempts to load the ospf shutdown config for the specified host and process (via napalm).
    :param minion: The target host
    :param process_number: The OSPF process number
    :param case: case-id for updating the current case
    :return: a dictionary containing the follow keys:
                result (bool), comment (str, a message for the user), already_configured (bool)
                loaded_config (str), diff (str)
    '''
    template_name = 'shutdown_ospf'
    template_source = 'router ospf {0}\n  shutdown\nend'.format(process_number)
    config = {'template_name': template_name, 'template_source': template_source}
    oatsdbhelpers.update_case(case, solution='Trying to apply shutdown to OSPF process {0}.'.format(process_number))
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def ospf_noshutdown(minion, process_number, case=None):
    '''
        Attempts to load the ospf no shutdown config for the specified host and process (via napalm).
        :param minion: The target host
        :param process_number: The OSPF process number
        :param case: case-id for updating the current case
        :return: a dictionary containing the follow keys:
                    result (bool), comment (str, a message for the user), already_configured (bool)
                    loaded_config (str), diff (str)
        '''
    template_name = 'shutdown_ospf'
    template_source = 'router ospf {0}\n  no shutdown\nend'.format(process_number)
    config = {'template_name': template_name, 'template_source': template_source}
    oatsdbhelpers.update_case(case, solution='Trying to apply no shutdown to OSPF process {0}.'.format(process_number))
    return __salt__['salt.execute'](minion, 'net.load_template', kwarg=config)

def check_device_connectivity(neighbors, host, case=None):
    '''
    executes pings from neighbors to the host

    :param neighbors: the hosts neighbors
    :param host: the host to check connectivity to
    :param case: case-id for updating the current case
    :return: if the host is connected to one of his neighbors or the master (bool)
    '''
    connected = False
    for neighbor in neighbors:
        connected = ping(neighbor, host, check_connectivity=True)
        oatsdbhelpers.update_case(case,
                                  solution='Checking connectivity from {0} to {1}. Result: {2}'
                                  .format(neighbor, host,str(bool(connected))))
        if connected:
            return connected
    return connected


def count_event(tag, error, amount, wait=10, case=None):
    '''
    Checks if a certain event occurs X amount of times in a
    given timeframe. Should be used asynchronous, since
    the method is blocking.
    :param tag: The event to count
    :param error: used for update_case
    :param amount: the required amount of events
    :param wait: the timeframe to wait for the events
    :param case: case-id for updating the current case
    :return: if the event occured atleast <amount> of times (bool)
    '''
    opts = salt.config.client_config('/etc/salt/master')

    event = salt.utils.event.get_event(
        'master',
        sock_dir=opts['sock_dir'],
        transport=opts['transport'],
        opts=opts)
    counter = 0
    timeout = time.time() + wait
    oatsdbhelpers.update_case(case, solution='Waiting for {0} {1} events.'.format(amount, error))
    while time.time() < timeout:
        if event.get_event(wait=3, tag=tag):
            counter += 1
    success = counter >= amount
    oatsdbhelpers.update_case(case, solution='Result: {0} events. Wait success: {1}.'.format(counter, success))
    return success
