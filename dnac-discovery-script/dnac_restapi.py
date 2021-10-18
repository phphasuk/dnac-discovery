#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

DNAC Discovery Script.

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


import urllib3
import requests
import json
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
import logging


class rest_api_lib:
    def __init__(self, dnac_ip, dnac_port, username, password):
        urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings
        self.dnac_ip = dnac_ip
        self.dnac_port = dnac_port
        self.username = username
        self.password = password
        self.token = self.get_token()


    def get_token(self):
        url = 'https://%s:%s/dna/system/api/v1/auth/token'%(self.dnac_ip, self.dnac_port)
        auth = HTTPBasicAuth(self.username, self.password)
        headers = {'content-type' : 'application/json'}
        try:
            response = requests.post(url, auth=auth, headers=headers, verify=False)
            response.raise_for_status()
            token = response.json()['Token']
            logging.info('Got Token from DNAC')
            logging.debug(f'Token: {token}')
            return token
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()


    def get_task_info(self, tid):
        headers = {
                'x-auth-token': self.token,
                'content-type': 'application/json'}
        url = f"https://{self.dnac_ip}:{self.dnac_port}/dna/intent/api/v1/task/{tid}"
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            info = response.json()['response']
            logging.info(f'Got Task Info for: {tid}')
            logging.debug(f'Take Info: {info}')
            return info
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()


    def get_discovery_info(self, did):
        headers = {
                'x-auth-token': self.token,
                'content-type': 'application/json'}
        url = f"https://{self.dnac_ip}:{self.dnac_port}/dna/intent/api/v1/discovery/{did}"
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            info = response.json()['response']
            logging.info(f'Got Discovery Info for: {did}')
            logging.debug(f'Take Info: {info}')
            return info
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()


    def get_discovery_result(self, did):
        headers = { 'x-auth-token': self.token,
                    'content-type': 'application/json' }
        url = f"https://{self.dnac_ip}:{self.dnac_port}/dna/intent/api/v1/discovery/{did}/network-device"
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            info = response.json()['response']
            logging.info(f'Got Discovery Result for: {did}')
            logging.debug(f'Take Info: {info}')
            return info
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()


    def delete_alldiscovery(self):
        headers = {
                'x-auth-token': self.token,
                'content-type': 'application/json'}
        url = f"https://{self.dnac_ip}:{self.dnac_port}/dna/intent/api/v1/discovery"
        try:
            response = requests.delete(url, headers=headers, verify=False)
            response.raise_for_status()
            logging.info(f'Delete all discovery tasks complete.')
            return
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()


    def add_discovery_node(self, node_info):
        headers = {
                'x-auth-token': self.token,
                'content-type': 'application/json'}
        mount_point = 'dna/intent/api/v1/discovery'
        url = "https://%s:%s/%s"%(self.dnac_ip, self.dnac_port, mount_point)
        payload = { "cdpLevel": 1,
                    "lldpLevel": 1,
                    "discoveryType": "SINGLE",
                    "protocolOrder": "ssh,telnet", }
        for key, value in node_info.items():
            if 'List' in key and key != "ipAddressList":
                payload[key] = [value]
            else:
                payload[key] = value
        logging.info(f'Adding discovery task for: {node_info["ipAddressList"]}')
        logging.debug(f'Adding discovery task payload: {payload}')
        try:
            response = requests.post(url=url, headers=headers, data=json.dumps(payload), verify=False)
            response.raise_for_status()
            info = response.json()['response']
            logging.info(f'Adding discovery task done for: {node_info["ipAddressList"]}')
            logging.debug(f'Adding discovery ta: {info}')
            return info['taskId']
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()


    def logout(self):
        """Logout from dnac"""
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'X-XSRF-TOKEN': self.token}
        url = "https://%s:%s/logout?nocache"%(self.dnac_ip, self.dnac_port)
        try:
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()
            logging.info(f'Logout from DNAC successful')
            logging.debug(f'Logout from DNAC successful response: {response}')
            return
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            raise SystemExit()
