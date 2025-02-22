"""
Config auditor. Runs before api startup and checks the included .conf file for
correctness and viability. Raises errors if errors occur.

Each *_check function covers a particular section of the config file and uses
the Config.get() function from actors/config.py to check if a value exists. If
not, an error is raised. Additional checks run for particular options to ensure
option values are set to proper values.

Background:
[section]
option: value
option: value

To-do:
    - Add warning for when an option is set but not needed.
"""

from configparser import NoOptionError
from config import Config

def valexists(section, option):
    """
    Checks if a value in a section exists, returns True if populated,
    False otherwise.
    """
    try:
        Config.get(section, option)
        return True
    except NoOptionError:
        return False


def general_check():
    """
    Checks that all section options are set correctly.
    All section options: 'TAG'.
    """
    section = 'general'

    # Raises error for required options
    req_options = ['TAG']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))


def logs_check():
    """
    Checks that all section options are set correctly.
    All section options: 'level', 'level.worker', 'level.docker_util',
    'level.spawner', 'level.controllers'.
    """
    section = 'logs'

    # Raises error for required options
    req_options = ['level']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))

    # Raises error if selected options are not set to ERROR or DEBUG
    err_debug_options = ['level', 'level.worker', 'level.docker_util',
                         'level.spawner', 'level.controllers']
    for option in err_debug_options:
        if valexists(section, option):
            if Config.get(section, option) not in ['ERROR', 'DEBUG']:
                raise ValueError('{}:{} should be set to ERROR or DEBUG'.format(section, option))



def store_check():
    """
    Checks that all section options are set correctly.
    All section options: 'mongo_host', 'mongo_port', 'mongo_user',
    'mongo_password'.
    """
    section = 'store'

    # Raises error for required options
    req_options = ['mongo_host', 'mongo_port']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))

    # Raises error if mongo_user or mongo_password is set without the other
    if valexists(section, 'mongo_user') ^ valexists(section, 'mongo_password'):
        raise ValueError('mongo_user and mongo_password must be set concurrently')


def rabbit_check():
    """
    Checks that all section options are set correctly.
    All section options: 'uri'
    """
    section = 'rabbit'

    # Raises error for required options
    req_options = ['uri']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))


def spawner_check():
    """
    Checks that all section options are set correctly.
    All section options: 'host_id', 'host_queues', 'host_ip',
    'abaco_conf_host_path', 'max_workers_per_host', 'max_workers_per_actor',
    'docker_network'.
    """
    section = 'spawner'

    # Raises error for required options
    req_options = ['host_id', 'host_queues', 'host_ip',
                   'max_workers_per_host', 'max_workers_per_host',
                   'max_workers_per_actor']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))


def docker_check():
    """
    Checks that all section options are set correctly.
    All section options: 'dd'
    """
    section = 'docker'

    # Raises error for required options
    req_options = ['dd']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))


def workers_check():
    """
    Checks that all section options are set correctly.
    All section options: 'init_count', 'max_run_time', 'mem_limit', 'max_cpus',
    'worker_ttl', 'auto_remove', 'generate_clients', 'global_mounts',
    'privileged_mounts', 'leave_containers', 'actor_uid', 'actor_gid',
    'use_tas_uid', 'socket_host_path_dir', 'fifo_host_path_dir'.
    """
    section = 'workers'

    # Raises error for required options
    req_options = ['init_count', 'max_run_time', 'max_cpus', 'worker_ttl',
                   'auto_remove', 'generate_clients', 'leave_containers',
                   'use_tas_uid', 'socket_host_path_dir', 'fifo_host_path_dir']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))

    # Raises error if 'auto_remove' is not set to true or false
    if Config.get(section, 'auto_remove') not in ['true', 'false']:
        raise ValueError('{}:{} should be set to true or false'.format(section, 'auto_remove'))

    # Raises error if 'generate_clients' is not set to True or False
    if Config.get(section, 'generate_clients') not in ['True', 'False']:
        raise ValueError('{}:{} should be set to True or False'.format(section, 'generate_clients'))

    # Raises error if 'leave_containers' is not set to True or False
    if Config.get(section, 'leave_containers') not in ['True', 'False']:
        raise ValueError('{}:{} should be set to True or False'.format(section, 'leave_containers'))

    # Raises error if 'use_tas_uid' is not set to True or False
    if Config.get(section, 'use_tas_uid') not in ['True', 'False']:
        raise ValueError('{}:{} should be set to True or False'.format(section, 'use_tas_uid'))

def web_check():
    """
    Checks that all section options are set correctly.
    All section options: 'access_control', 'user_role', 'accept_nonce',
    'tenant_name', 'apim_public_key', 'show_traceback', 'log_ex', 'case',
    'max_content_length', 'all_queues'.
    """
    section = 'web'

    # Raises error for required options
    req_options = ['access_control', 'show_traceback', 'log_ex', 'case',
                   'max_content_length', 'all_queues']
    for option in req_options:
        if not valexists(section, option):
            raise ValueError('{}:{} should be set.'.format(section, option))

    # Raises error if 'access_control' is not set to jwt or none
    if Config.get(section, 'access_control') not in ['jwt', 'none']:
        raise ValueError('{}:{} should be set to jwt or none'.format(section, 'access_control'))

    # Raises error if jwt access control is used and 'apim_public_key' is not set
    if Config.get(section, 'access_control') == 'jwt':
        if not valexists('web', 'apim_public_key'):
            raise ValueError("{}:{} must be set if 'access_control' is set to 'jwt'"
                             .format(section, 'apim_public_key'))

    # Raises error if there is no access control and 'accept_nonce' or 'tenant_name' are not set
    if Config.get(section, 'access_control') == 'none':
        for none_dep in ['accept_nonce', 'tenant_name']:
            if not valexists('web', none_dep):
                raise ValueError("{}:{} must be set if 'access_control' is set to 'none'"
                                 .format(section, none_dep))

    # Raises error if 'accept_nonce' is not set to True or False
    if valexists(section, 'accept_nonce'):
        if Config.get(section, 'accept_nonce') not in ['True', 'False']:
            raise ValueError('{}:{} should be set to True or False'.format(section, 'accept_nonce'))

    # Raises error if 'case' is not set to camel or snake
    if Config.get(section, 'case') not in ['camel', 'snake']:
        raise ValueError('{}:{} should be set to camel or snake'.format(section, 'case'))

    # Raises error if 'show_traceback' is not set to true or false
    if Config.get(section, 'show_traceback') not in ['true', 'false']:
        raise ValueError('{}:{} should be set to true or false'.format(section, 'show_traceback'))

    host_queues = Config.get('spawner', 'host_queues').replace(',', '').split()
    all_queues = Config.get('web', 'all_queues').replace(',', '').split()
    if not set(host_queues).issubset(all_queues):
        raise ValueError("'spawner:hosts_queues' not subset of 'web:all_queues'.")

def run_all_checks():
    """
    Run all section checks, comment out a function if something has changed,
    or been deprecated. Easy to add sections for future use.
    """
    general_check()
    logs_check()
    store_check()
    rabbit_check()
    spawner_check()
    docker_check()
    workers_check()
    web_check()

if __name__ == "__main__":
    run_all_checks()
    print('Config checks passed.')
