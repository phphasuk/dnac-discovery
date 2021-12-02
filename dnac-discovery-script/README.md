# DNAC Discovery Script

*DNAC Discovery Script*

---

**ToDo's:**

- Any comments, Please email to me @ phphasuk@cisco.com

---

## Motivation

In some specific use cases, the customer needs to add the discovery job per device. If there are many devices, it will be a cumbersome task to do it using GUI. The productive way to do it is with the automation script and API. This script intends to give the customer an example of using API to add the discovery jobs with specific steps and prerequisites. If the customers use the different processes, the customer can modify the script to support their intent.

Adding "assign to site" function to move unassigned devices to site.

## Features

- Load the discovery parameters from the CSV file
- Add the discovery jobs to DNAC
- Check the added discovery tasks's status
- Check the added discovery jobs's status
- Get the discovery jobs's result, save them into the CSV file, and print them in the terminal screen
- Move unassigned devices to site from the ip/site csv file

## Technologies & Frameworks Used

This is Cisco Sample Code using Python Programming, supporting for DNAC Discovery feature.

**Cisco Products & Services:**

- DNA Center

## Prerequisite steps

This script supports the specific discovery process using DNAC. Before running this script, we need the prerequisite steps below before adding the discovery tasks into DNAC.

- Device Discovery Parameters in CSV file
- Device IP/Site parameters in CSV file

## File Description

File Description:
- "dnac_config.py" – Configuration File (DNAC IP / Port Number)
- "utils.py" – CSV utility functions
- "dnac_restapi.py" – DNAC API functions
- "dnac_discovery.py" – DNAC Discovery main script
- "Requirements.txt" – Needed python modules
- "discovery_data.csv" - Devices Discovery Parameters file in CSV format
- "task_result.csv" - tasks's result output file in CSV format
- "discovery_result.csv" - discovery jobs's result output file in CSV format
- "assign_site_data.csv" - Device IP and Site parameters file in CSV format
- "assign_site_result.csv" - assign site's result output file in CSV format

## "discovery_data.csv" File
Needed Parameters:
- No: discovery id in the script ex. 1,2,3,...
- name: discovery job's name in DNAC
- enablePasswordList: device's enable password
- ipAddressList: device's management ip address
- passwordList: device's login user's password
- snmpAuthPassphrase: snmp v3's Auth Passphrase
- snmpAuthProtocol: snmp v3's Auth Protocol
- snmpMode: snmp v3's Auth Mode
- snmpPrivPassPhrase: snmp v3's Priviledge Pass Phrase
- snmpPrivProtocol: snmp v3's Priviledge Protocol
- snmpROCommunity: snmp's read only community
- snmpRWCommunity: snmp's read/write community
- userNameList: device's login username

These data will be converted and put in the added discovery job API's payload as below.
```
{'cdpLevel': 1,
 'lldpLevel': 1,
 'discoveryType': 'SINGLE',
 'protocolOrder': 'ssh,telnet',
 'No': '2',
 'name': 'test109',
 'enablePasswordList': ['CiscoDNA1'],
 'ipAddressList': '192.168.200.231',
 'passwordList': ['C!sc0123'],
 'snmpAuthPassphrase': 'DNAC-ACCESS',
 'snmpAuthProtocol': 'SHA',
 'snmpMode': 'AUTHPRIV',
 'snmpPrivPassphrase': 'POD2-SNMPv3',
 'snmpPrivProtocol': 'AES128',
 'snmpROCommunity': 'public',
 'snmpRWCommunity': 'private',
 'userNameList': ['css']}
```

## "assign_site_data.csv" File
Needed Parameters:
- No: assign id in the script ex. 1,2,3,...
- ip: unassigned device's ip address in DNAC
- site: site name in DNAC

## Installation

- Install the required python module
```
pip install -r requirements.txt
```

- Configure DNAC Server information in dnac_config.py
```
DNAC_IP = '<DNA's IP Address>'
DNAC_PORT = '<DNAC's HTTP Port Number>"
```

## Usage

Script usage arguments:
```
$ python dnac_discovery.py --help

usage: dnac_discovery.py [-h] [--file FILE] [--mode MODE]

Device Discovery.

optional arguments:
  -h, --help   show this help message and exit
  --file FILE  Devices Information in CSV format, using comma as delimiter
  --mode MODE  add, delete, assign
```
Adding the discovery jobs:
```
$ python dnac_discovery.py --mode add --file discovery_data.csv
```
Delete all discovery jobs:
```
$ python dnac_discovery.py --mode delete

```
Assign deivce to site:
```
$ python dnac_discovery_py --mode assign --file assign_site_data.csv
```

## Authors & Maintainers

- Phithakkit Phasuk <phphasuk@cisco.com>

## Credits

- https://developer.cisco.com/

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
