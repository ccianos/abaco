# Functional test suite for abaco.
# Start the local development abaco stack and run these tests with py.test from the cwd.

# Notes:
# 1. Running the tests against the docker-compose-local.yml instance (using local-dev.conf) will use an access_control
#    of none and the tenant configured in local-dev.conf (dev_staging) for all requests (essentially ignore headers).
#
# 2.

import os
import time

import pytest
import requests
import json

base_url = os.environ.get('base_url', 'http://localhost:8000')

# #################
# registration API
# #################

@pytest.fixture(scope='session')
def headers():
    jwt = os.environ.get('jwt', open('jwt').read())
    if jwt:
        jwt_header = os.environ.get('jwt_header', 'X-Jwt-Assertion-AGAVE-PROD')
        headers = {jwt_header: jwt}
    else:
        token = os.environ.get('token', '')
        headers = {'Authorization': 'Bearer {}'.format(token)}
    return headers

def test_remove_initial_actors(headers):
    url = '{}/actors'.format(base_url)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    for act in result:
        url = '{}/actors/{}'.format(base_url, act.get('id'))
        rsp = requests.delete(url, headers=headers)
        basic_response_checks(rsp)

def basic_response_checks(rsp):
    assert rsp.status_code in [200, 201]
    assert  'application/json' in rsp.headers['content-type']
    data = json.loads(rsp.content)
    assert 'msg' in data.keys()
    assert 'status' in data.keys()
    assert 'result' in data.keys()
    assert 'version' in data.keys()
    return data['result']

def test_list_actors(headers):
    url = '{}/{}'.format(base_url, '/actors')
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 0

def test_register_actor(headers):
    url = '{}/{}'.format(base_url, '/actors')
    data = {'image': 'jstubbs/abaco_test', 'name': 'abaco_test_suite'}
    rsp = requests.post(url, data=data, headers=headers)
    result = basic_response_checks(rsp)
    assert 'description' in result
    assert 'tenant' in result
    assert result['image'] == 'jstubbs/abaco_test'
    assert result['name'] == 'abaco_test_suite'
    assert result['id'] is not None

def get_actor_id(headers, name='abaco_test_suite'):
    url = '{}/{}'.format(base_url, '/actors')
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    for k in result:
        if k.get('name') == name:
            return k.get('id')
    # didn't find the test actor
    assert False

def test_list_actor(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert 'description' in result
    assert 'tenant' in result
    assert result['image'] == 'jstubbs/abaco_test'
    assert result['name'] == 'abaco_test_suite'
    assert result['id'] is not None

def test_actor_is_ready(headers):
    count = 0
    actor_id = get_actor_id(headers)
    while count < 10:
        url = '{}/actors/{}'.format(base_url, actor_id)
        rsp = requests.get(url, headers=headers)
        result = basic_response_checks(rsp)
        if result['status'] == 'READY':
            return
        time.sleep(3)
        count += 1
    assert False


# ###################
# executions and logs
# ###################

def test_list_executions(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/executions'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result.get('ids')) == 0

def test_list_messages(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/messages'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert result.get('messages') == 0

def test_execute_actor(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/messages'.format(base_url, actor_id)
    data = {'message': 'testing execution'}
    rsp = requests.post(url, data=data, headers=headers)
    result = basic_response_checks(rsp)
    assert result.get('msg')  == 'testing execution'
    # check for the execution to complete
    count = 0
    while count < 10:
        time.sleep(3)
        url = '{}/actors/{}/executions'.format(base_url, actor_id)
        rsp = requests.get(url, headers=headers)
        result = basic_response_checks(rsp)
        ids = result.get('ids')
        if ids:
            assert len(ids) == 1
            assert ids[0] is not None
            assert result.get('total_executions') == 1
            assert result.get('total_cpu')
            assert result.get('total_io')
            assert result.get('total_runtime')
            return
        count += 1
    assert False

def test_list_execution_logs(headers):
    actor_id = get_actor_id(headers)
    # get execution id
    url = '{}/actors/{}/executions'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    exec_id = result.get('ids')[0]
    url = '{}/actors/{}/executions/{}/logs'.format(base_url, actor_id, exec_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert 'Contents of MSG: testing execution' in result
    assert 'PATH' in result

def test_update_actor(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}'.format(base_url, actor_id)
    data = {'image': 'jstubbs/abaco_test2'}
    rsp = requests.put(url, data=data, headers=headers)
    result = basic_response_checks(rsp)
    assert 'description' in result
    assert 'tenant' in result
    assert result['image'] == 'jstubbs/abaco_test2'
    assert result['name'] == 'abaco_test_suite'
    assert result['id'] is not None



# ################
# admin API
# ################

def test_list_workers(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/workers'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) > 0
    # get the first worker
    worker = result[result.keys()[0]]
    assert worker.get('image') == 'jstubbs/abaco_test'
    assert worker.get('status') == 'READY'
    assert worker.get('location')
    assert worker.get('cid')
    assert worker.get('last_execution')
    assert worker.get('ch_name')

def test_add_worker(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/workers'.format(base_url, actor_id)
    rsp = requests.post(url, headers=headers)
    basic_response_checks(rsp)
    time.sleep(8)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 2

def test_delete_worker(headers):
    # get the list of workers
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/workers'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)

    # delete the first one
    id = result[result.keys()[0]].get('ch_name')
    url = '{}/actors/{}/workers/{}'.format(base_url, actor_id, id)
    rsp = requests.delete(url, headers=headers)
    result = basic_response_checks(rsp)
    time.sleep(4)

    # get the update list of workers
    url = '{}/actors/{}/workers'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 1

def test_list_permissions(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/permissions'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 1

def test_add_permissions(headers):
    actor_id = get_actor_id(headers)
    url = '{}/actors/{}/permissions'.format(base_url, actor_id)
    data = {'user': 'tester', 'level': 'UPDATE'}
    rsp = requests.post(url, data=data, headers=headers)
    result = basic_response_checks(rsp)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 2


# ##############################
# tenancy - tests for bleed over
# ##############################

def test_tenant_list_actors():
    # passing another tenant should result in 0 actors.
    headers = {'tenant': 'abaco_test_suite_tenant'}
    url = '{}/{}'.format(base_url, '/actors')
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 0

def test_tenant_register_actor():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    url = '{}/{}'.format(base_url, '/actors')
    data = {'image': 'jstubbs/abaco_test', 'name': 'abaco_test_suite_other_tenant'}
    rsp = requests.post(url, data=data, headers=headers)
    result = basic_response_checks(rsp)
    assert 'description' in result
    assert 'tenant' in result
    assert result['image'] == 'jstubbs/abaco_test'
    assert result['name'] == 'abaco_test_suite_other_tenant'
    assert result['id'] is not None

def test_tenant_actor_is_ready():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    count = 0
    actor_id = get_actor_id(headers, name='abaco_test_suite_other_tenant')
    while count < 10:
        url = '{}/actors/{}'.format(base_url, actor_id)
        rsp = requests.get(url, headers=headers)
        result = basic_response_checks(rsp)
        if result['status'] == 'READY':
            return
        time.sleep(3)
        count += 1
    assert False

def test_tenant_list_registered_actors():
    # passing another tenant should result in 1 actor.
    headers = {'tenant': 'abaco_test_suite_tenant'}
    url = '{}/{}'.format(base_url, '/actors')
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) == 1

def test_tenant_list_actor():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    actor_id = get_actor_id(headers, name='abaco_test_suite_other_tenant')
    url = '{}/actors/{}'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert 'description' in result
    assert 'tenant' in result
    assert result['image'] == 'jstubbs/abaco_test'
    assert result['name'] == 'abaco_test_suite_other_tenant'
    assert result['id'] is not None

def test_tenant_list_executions():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    actor_id = get_actor_id(headers, name='abaco_test_suite_other_tenant')
    url = '{}/actors/{}/executions'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result.get('ids')) == 0

def test_tenant_list_messages():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    actor_id = get_actor_id(headers, name='abaco_test_suite_other_tenant')
    url = '{}/actors/{}/messages'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert result.get('messages') == 0

def test_tenant_list_workers():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    actor_id = get_actor_id(headers, name='abaco_test_suite_other_tenant')
    url = '{}/actors/{}/workers'.format(base_url, actor_id)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    assert len(result) > 0
    # get the first worker
    worker = result[result.keys()[0]]
    assert worker.get('image') == 'jstubbs/abaco_test'
    assert worker.get('status') == 'READY'
    assert worker.get('location')
    assert worker.get('cid')
    assert worker.get('ch_name')


# ##############
# Clean up
# ##############

def test_remove_final_actors(headers):
    url = '{}/actors'.format(base_url)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    for act in result:
        url = '{}/actors/{}'.format(base_url, act.get('id'))
        rsp = requests.delete(url, headers=headers)
        result = basic_response_checks(rsp)

def test_tenant_remove_final_actors():
    headers = {'tenant': 'abaco_test_suite_tenant'}
    url = '{}/actors'.format(base_url)
    rsp = requests.get(url, headers=headers)
    result = basic_response_checks(rsp)
    for act in result:
        url = '{}/actors/{}'.format(base_url, act.get('id'))
        rsp = requests.delete(url, headers=headers)
        result = basic_response_checks(rsp)