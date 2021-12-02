#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

DNAC Discovery and Site Assignment Script.

Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Phithakkit Phasuk"
__email__ = "phphasuk@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2021 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import json
import argparse
from argparse import RawTextHelpFormatter
import getpass
from dnac_restapi import rest_api_lib
from utils import csv_to_dict, dict_to_csv, print_csv
from dnac_config import DNAC_IP, DNAC_PORT
import time
import re
import logging


def main():
    logging.basicConfig(
    #filename='application_run.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('starting the program.')
    task_info = {}
    discovery_result = {}
    discId_pattern = r'^([0-9]+)$'
    parser = argparse.ArgumentParser(description='Device Discovery.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--file', dest='file',
                        help='Devices Information in CSV format, using comma as delimiter')
    parser.add_argument('--mode', dest='mode',
                        help='add, delete, assign')
    args = parser.parse_args()
    print('='*20)
    username = input('Username: ')
    password = getpass.getpass()
    print('='*20)
    logging.info('logging to DNA Center.')
    dnac = rest_api_lib(DNAC_IP, DNAC_PORT, username, password)
    if args.mode == 'add':
        logging.info('loading CSV data file.')
        nodes_list = csv_to_dict(args.file)
        total_task = len(nodes_list)
        fail_task = 0
        success_task = 0
        complete_discovery = 0
        logging.info('finish loading CSV data file.')
        logging.info('adding discovery tasks.')
        for id, node_info in nodes_list.items():
            task_info[id] = {}
            task_info[id]['Name'] = node_info['name']
            task_info[id]['taskId'] = dnac.add_discovery_node(node_info)
            task_info[id]['taskResult'] = 'WAITING'
            discovery_result[id] = {}
            discovery_result[id]['Name'] = node_info['name']
            discovery_result[id]['taskResult'] = 'WAITING'
        logging.info('adding discovery tasks done.')
        logging.info('checking status for discovery tasks .')
        while True:
            time.sleep(5)
            for id in nodes_list:
                if 'tStatus' in task_info[id]:
                    if task_info[id]['tStatus'] == 'checked':
                        continue
                else:
                    logging.info(f'getting task info for id: {id}, taskId: {task_info[id]["taskId"]}.')
                    task_info[id]['taskInfo'] = dnac.get_task_info(task_info[id]['taskId'])
                    if task_info[id]['taskInfo']['isError'] == True and discovery_result[id]['taskResult'] == 'WAITING':
                        task_info[id]['taskResult'] = 'FAIL'
                        task_info[id]['tStatus'] = 'checked'
                        task_info[id]['failureReason'] = task_info[id]['taskInfo']['failureReason']
                        discovery_result[id]['discId'] = ''
                        discovery_result[id]['taskResult'] = 'FAIL'
                        discovery_result[id]['taskId'] = task_info[id]['taskId']
                        fail_task += 1
                        logging.info(f'task id: {id} is executed, but fail. {task_info[id]["tStatus"]}')
                        logging.info(f'fail task: {fail_task}')
                    else:
                        match = re.search(discId_pattern, task_info[id]['taskInfo']['progress'])
                        if match and discovery_result[id]['taskResult'] == 'WAITING':
                            task_info[id]['taskResult'] = 'SUCCESS'
                            task_info[id]['tStatus'] = 'checked'
                            task_info[id]['failureReason'] = ''
                            discovery_result[id]['discId'] = match.group()
                            discovery_result[id]['taskResult'] = 'SUCCESS'
                            discovery_result[id]['taskId'] = task_info[id]['taskId']
                            success_task += 1
                            logging.info(f'Task id: {id} is executed, and success. {task_info[id]["tStatus"]}')
                            logging.info(f'Successful task: {success_task}')
                        elif match and discovery_result[id]['taskResult'] == 'SUCCESS':
                            continue
                        else:
                            continue
            if total_task == success_task + fail_task:
                logging.info(f'total_task: {total_task}, success_task: {success_task}, fail_task: {fail_task}')
                logging.info(f'total_task({total_task}) = succes_task({success_task}) + fail_task({fail_task})')
                break
        logging.info('all discovery tasks are excecuted.')
        total_discovery = total_task - fail_task
        logging.info(f'total_discovery({total_discovery}) = total_task({total_task}) - fail_task({fail_task})')
        logging.info(f'total_discovery: {total_discovery}')
        logging.debug(f'task_info: {json.dumps(task_info, indent=2)}')
        logging.debug(f'discovery_result: {json.dumps(discovery_result, indent=2)}')
        logging.info('checking discovery status.')
        while True:
            time.sleep(5)
            for id in nodes_list:
                if discovery_result[id]['discId']:
                    if 'dStatus' in discovery_result[id]:
                        if discovery_result[id]['dStatus'] == 'checked':
                            continue
                    else:
                        logging.info(f'getting discovery info for: {id}, discId: {discovery_result[id]["discId"]}')
                        discovery_result[id]['discInfo'] = dnac.get_discovery_info(discovery_result[id]['discId'])
                        discStatus = discovery_result[id]['discInfo']['discoveryStatus']
                        discCondition = discovery_result[id]['discInfo']['discoveryCondition']
                        logging.info(f'discovery id: {id}, discStatus={discStatus}, discCondition={discCondition}')
                        if discStatus != 'Inactive' and discCondition != 'Complete':
                            continue
                        elif discStatus == 'Inactive' and discCondition == 'Complete':
                            complete_discovery += 1
                            discovery_result[id]['dStatus'] = 'checked'
                            logging.info(f'discovery id: {id} is complete. {discovery_result[id]["dStatus"]}')
                            logging.info(f'complete discovery: {complete_discovery}')
                        else:
                            continue
                else:
                    continue
            if complete_discovery == total_discovery:
                logging.info(f'complete_discovery: {complete_discovery} = total_discovery: {total_discovery}')
                break
        logging.info('All discoveries are complete.')
        logging.debug(f'task_info: {json.dumps(task_info, indent=2)}')
        logging.debug(f'discovery_result: {json.dumps(discovery_result, indent=2)}')
        logging.info('starting prepare discovery_result for csv file.')
        for id in nodes_list:
            if discovery_result[id]['discId']:
                logging.info(f'getting discovery result for id: {id}.')
                discovery_result[id]['discResult'] = dnac.get_discovery_result(discovery_result[id]['discId'])
                logging.debug(f'{json.dumps(discovery_result[id], indent=2)}')
                if discovery_result[id]['discResult'] != []:
                    if isinstance(discovery_result[id]['discResult'], list):
                        discovery_result[id]['IpAddress'] = discovery_result[id]['discResult'][0]['managementIpAddress']
                        discovery_result[id]['Status'] = discovery_result[id]['discResult'][0]['reachabilityStatus'].upper()
                        #discovery_result[id]['reachabilityFailureReason'] = discovery_result[id]['discResult'][0]['reachabilityFailureReason']
                        discovery_result[id]['ping'] = discovery_result[id]['discResult'][0]['pingStatus']
                        discovery_result[id]['snmp'] = discovery_result[id]['discResult'][0]['snmpStatus']
                        discovery_result[id]['cli'] = discovery_result[id]['discResult'][0]['cliStatus']
                        discovery_result[id]['http'] = discovery_result[id]['discResult'][0]['httpStatus']
                        discovery_result[id]['netconf'] = discovery_result[id]['discResult'][0]['netconfStatus']
                        discovery_result[id]['invCollection'] = discovery_result[id]['discResult'][0]['inventoryCollectionStatus']
                        discovery_result[id]['invReachability'] = discovery_result[id]['discResult'][0]['inventoryReachabilityStatus']
                    else:
                        discovery_result[id]['IpAddress'] = discovery_result[id]['discResult']['managementIpAddress']
                        discovery_result[id]['Status'] = discovery_result[id]['discResult']['reachabilityStatus'].upper()
                        #discovery_result[id]['reachabilityFailureReason'] = discovery_result[id]['discResult']['reachabilityFailureReason']
                        discovery_result[id]['ping'] = discovery_result[id]['discResult']['pingStatus']
                        discovery_result[id]['snmp'] = discovery_result[id]['discResult']['snmpStatus']
                        discovery_result[id]['cli'] = discovery_result[id]['discResult']['cliStatus']
                        discovery_result[id]['http'] = discovery_result[id]['discResult']['httpStatus']
                        discovery_result[id]['netconf'] = discovery_result[id]['discResult']['netconfStatus']
                        discovery_result[id]['invCollection'] = discovery_result[id]['discResult']['inventoryCollectionStatus']
                        discovery_result[id]['invReachability'] = discovery_result[id]['discResult']['inventoryReachabilityStatus']
                else:
                    logging.info(f'Got discovery result for id: {id}, Result is None. Please check DNAC.')
                    discovery_result[id]['IpAddress'] = ''
                    discovery_result[id]['Status'] = ''
                    #discovery_result[id]['reachabilityFailureReason'] = ''
                    discovery_result[id]['ping'] = ''
                    discovery_result[id]['snmp'] = ''
                    discovery_result[id]['cli'] = ''
                    discovery_result[id]['http'] = ''
                    discovery_result[id]['netconf'] = ''
                    discovery_result[id]['invCollection'] = ''
                    discovery_result[id]['invReachability'] = ''
            else:
                discovery_result[id]['IpAddress'] = ''
                discovery_result[id]['Status'] = ''
                #discovery_result[id]['reachabilityFailureReason'] = ''
                discovery_result[id]['ping'] = ''
                discovery_result[id]['snmp'] = ''
                discovery_result[id]['cli'] = ''
                discovery_result[id]['http'] = ''
                discovery_result[id]['netconf'] = ''
                discovery_result[id]['invCollection'] = ''
                discovery_result[id]['invReachability'] = ''
        logging.info('complete prepare discovery_result for csv file.')
        logging.debug(f'discovery_result: {json.dumps(discovery_result, indent=2)}')
        logging.info('logging out from DNAC.')
        dnac.logout()
        logging.info('saving task_result.csv.')
        dict_to_csv(task_info,
                    'task_result.csv',
                    'Name',
                    'taskId',
                    'taskResult',
                    'failureReason')
        logging.info('saving discovery_result.csv.')
        dict_to_csv(discovery_result,
                    'discovery_result.csv',
                    'Name',
                    'discId',
                    'IpAddress',
                    'Status',
                    'ping',
                    'snmp',
                    'cli',
                    'http',
                    'netconf',
                    'invCollection',
                    'invReachability')
        print_csv('task_result.csv', 165)
        print_csv('discovery_result.csv', 165)
    elif args.mode == 'delete':
        logging.info('Deleting all discovery tasks.')
        dnac.delete_alldiscovery()
        logging.info('logging out from DNAC.')
        dnac.logout()
    elif args.mode == 'assign':
        nodes_list = csv_to_dict(args.file)
        for item in nodes_list:
            site_id = dnac.get_siteid_by_name(nodes_list[item]['site'])
            device_ip = nodes_list[item]['ip']
            nodes_list[item]['executionStatus'], nodes_list[item]['executionError'] = dnac.assign_device_to_site(site_id, device_ip)
        print(json.dumps(nodes_list, indent=2))
        logging.info('saving assign_site_result.csv.')
        dict_to_csv(nodes_list,
                    'assign_site_result.csv',
                    'ip',
                    'site',
                    'executionStatus',
                    'executionError')
        logging.info('logging out from DNAC.')
        dnac.logout()


if __name__ == '__main__':
    main()
