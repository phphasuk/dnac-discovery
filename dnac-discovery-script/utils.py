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


import logging
import csv


def csv_to_dict(csvFile):
    """
    converts csvfile to dictDataionary data
    :param csvFile
    :return key, distionary
    """
    with open(csvFile, 'r') as f:
        dictData = {}
        key = []
        id = 1
        csvdata = csv.reader(f, delimiter=',')
        key = next(csvdata)
        for row in csvdata:
            dictData[id] = {}
            for i in range(len(key)):
                dictData[id][key[i]] = row[i]
            id += 1
    return dictData


def dict_to_csv(dictData, csvfile, *args):
    """
    converts dictionary to csv file, only the first level data supported
    :param dictionary, csvfile name, included dictDataionary keys
    :return
    """
    with open(csvfile, 'w') as f:
        print(f'id,{",".join(args)}', file=f)
        for id, value in dictData.items():
            csv_line = [str(id)]
            for key in args:
                csv_line.append(value[key])
            print(f'{",".join(csv_line)}', file=f)
    return


def print_csv(csvFile, max_len):
    """
    Print CSV file
    :param CSV file, Maximum line length
    :return
    """
    with open(csvFile, 'r') as f:
        print('='*max_len)
        csvdata = csv.reader(f, delimiter=',')
        column_name = next(csvdata)
        num_column = len(column_name)
        max_charlen = []
        for i in range(num_column):
            max_charlen.append(len(column_name[i]))
        for row in csvdata:
            for i in range(num_column):
                if len(row[i]) > max_charlen[i]:
                    max_charlen[i] = len(row[i])
        f.seek(0)
        row_num = 1
        for row in csvdata:
            line = ''
            for i in range(num_column):
                column_width = max_charlen[i] + 2
                line = line + '{0:<{column_width}}'.format(row[i], column_width=column_width)
            print(line)
            if row_num == 1:
                print('-'*max_len)
            row_num += 1
        print('='*max_len)
    return
