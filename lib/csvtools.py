#!/usr/bin/env python

import os
import sys


def dict_to_csv(comps, filename):
    ## print column headings then all attributes for each company
    f = open(filename, 'wb')   
    
    columns = [x for x in comps[comps.keys()[0]].keys() if x != 'name']
    columns = ['name'] + columns

    f.write(','.join(columns) + '\n')
    for k,v in comps.items():
        for column in columns:
            f.write('"' + v[column] + '"' + ',')
        f.write('\n')
    
    f.close()
