#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 31 23:57:15 2022

@author: clarelin
"""



from harmony_checker import Harmony_checker

file = 'harmony_sample_3'
file_path = f'./data/xml/{file}.xml'
file_output_path = f'./output/{file}_output.xlsx'

file_path_xlsx = f'./data/xlsx/{file}.xlsx'

hc = Harmony_checker(file_path)
hc.run()
hc.output(file_output_path)
