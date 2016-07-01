#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Assemble Data from Census, City Land Use and other sources into a master Fire csv
"""
from ast import literal_eval
import csv
csv.field_size_limit(320000)


def get_element_ind(labels, tag):
    # Find the index where a given label occurs
    return [i for i in range(len(labels)) if labels[i] == tag][0]

def get_select_inds(list_data, inds):
    # down select data on the basis of a list of indecis
    return [item for i, item in enumerate(list_data) if i in inds]

#
def string2float(*args):
    element = args[0]
    if len(args) == 1:
        default = float('NaN')
    else:
        default = float(args[1])
    try:
        return float(element)
    except ValueError:
        return float(default)

# load a csv file:
def loadcsv2list(file_name):
    out = []
    with open(file_name, 'rb') as b:
        reader = csv.reader(b)
        for row in reader:
            out.append(row)
    return out

'''def merge_listlist(l1,l2):
    # takes two equal length lists of lists and combines the sublists for each index
    l12 = []
    for i in range(len(l1)):
        tmp = l1[i]
        for j in range(len(l2[i])):
            tmp.insert(len(tmp),l2[i][j])
        l12.append(tmp)
    return l12
'''
def merge_listlist(l1,l2):
    # takes two equal length lists of lists and combines the sublists for each index
    l12 = []
    for i in range(len(l1)):
        l12.append(l1[i]+l2[i])
    return l12

def header_data_combine(headers, data):
    tmp = data
    tmp.insert(0,headers)
    return tmp




# root_dir = '/Users/changlab/Documents/changrepo/matlab/analysis/Ishihara/Fire/Data/'
root_dir = '../input/'
fire_data_csv = 'Fire_Incidents.csv'
census_coords_data_csv = 'building_coords_copy.csv'
property_tax_csv = 'Historic_Secured_Property_Tax_Rolls.csv'
census_tract_data_csv = 'census/sf_census_data_rows.csv'


property_tax_data = loadcsv2list(root_dir+property_tax_csv)
lot_num = range(1,len(property_tax_data)) # (note first row is header data)

census_coords_data = loadcsv2list(root_dir+census_coords_data_csv)
#census_coords_data = [i for i in census_coords_data if i != '']
lot_num_census = [string2float(x[3][1:-1]) for x in census_coords_data[1:]] # The 4th column (delisted) of the non deader data
tract_census = [x[2] for x in census_coords_data[1:]]

# clear elements of property tax that are not on the census (vacant lots in the ocean (dead piers))
property_tax_data_restrict = [property_tax_data[int(i)] for i in lot_num_census] # eliminates header as well
lot_num_restrict = [lot_num[int(x)-1] for x in lot_num_census] # should be the same as lot_num_census

property_tax_data_restrict.insert(0,property_tax_data[0])
tract_census.insert(0,'tract')
tract_census = [[i] for i in tract_census]
property_tax_tract = merge_listlist(property_tax_data_restrict, tract_census)

property_tax_tract_headers = property_tax_tract[0]
property_tax_tract_data = property_tax_tract[1:]




## load census_data and add

census_data = loadcsv2list(root_dir + census_tract_data_csv)
census_data_header = census_data[0]
census_data = census_data[1:]
census_tract_ind = get_element_ind(census_data_header, 'tract')

master_header = property_tax_tract_headers
master_header = master_header + census_data_header
master_data = []
for i in range(len(property_tax_tract_data)):
    property_tract_num = string2float(tract_census[i][0])
    census_data_row = [x for x in census_data if string2float(x[census_tract_ind]) == property_tract_num]
    if len(census_data_row) != 0:
        master_data.append(property_tax_tract_data[i] + census_data_row[0])

## building locations:
address_master_ind =  get_element_ind(master_header, 'Property Location')
address_master = [x[address_master_ind] for x in master_data]
st_master = [x.split(' ')[2].lower() for x in address_master]
num_master = [x.split(' ')[1].lower() for x in address_master]

lat_long_master_ind = get_element_ind(master_header, 'Location')
latlong_master = [literal_eval(x[lat_long_master_ind]) for x in master_data]

## Fire data
fire_data = loadcsv2list(root_dir + fire_data_csv)
fire_headers = fire_data[0]
fire_data = fire_data[1:]

## Restrict to building fires:
situation_col =  get_element_ind(fire_headers, 'Primary Situation')
# code 111 is for building fires:
building_fire_inds = [i for i, row in enumerate(fire_data) if '111' in row[situation_col]]
fire_data = get_select_inds(fire_data, building_fire_inds)

address_fire = [x[get_element_ind(fire_headers, 'Address')].lower() for x in fire_data]
## FUCK SFO!
fire_data = [x for i, x in enumerate(fire_data) if 'airport' not in address_fire[i]]
address_fire = [x[get_element_ind(fire_headers, 'Address')].lower() for x in fire_data]
## I don't know the address (two instances, probably fine to drop)
known_address_inds= [i for i, x in enumerate(address_fire) if len(x.split(' '))> 1]
fire_data = get_select_inds(fire_data, known_address_inds)
address_fire = get_select_inds(address_fire, known_address_inds)

st_fire = [x.split(' ')[1].lower() for x in address_fire]
num_fire = [x.split(' ')[0].lower() for x in address_fire]

latlong_fire = [x[get_element_ind(fire_headers, 'Location')] for x in fire_data]
# not in gps form - kinda sucks

## Patch together fire data into master data:
for i in range(len(fire_data)):
    st_inds = [j for j, x in enumerate(st_master) if x == st_fire[i]]
    num_inds = [j for j, x in enumerate(num_master) if x == num_fire[i]]
    possible_inds = list(set(st_inds).intersection(num_inds))
    if len(possible_inds) > 1:
        if len(latlong_fire[i]) > 1:
            coord = literal_eval(latlong_fire[i])
            possible_coords = get_select_inds(latlong_master, possible_inds)
            dists = [abs(coord[0] - c[0]) + abs(coord[1]-c[1]) for c in possible_coords]
            closest_ind = [j for j, x in enumerate(dists) if x == min(dists)][0]
            master_data[possible_inds[closest_ind]] = master_data[possible_inds[0]] + fire_data[i]
    elif len(possible_inds) == 1:
        master_data[possible_inds[0]] = master_data[possible_inds[0]] + fire_data[i]





master_header = master_header + fire_headers
master_table = header_data_combine(master_header, master_data)

with open(root_dir + 'fire_data_master.csv', 'wb') as f:
    writer = csv.writer(f,)
    writer.writerows(master_table)

test = loadcsv2list(root_dir + 'fire_data_master.csv')


'''
## Duplicate entries to weight fire data equally to non fire data:
row_lens = [len(x) for x in master_data]
fire_inds = len([x for x in row_lens if x == max(row_lens)])

num_fires = len(fire_inds)
num_nonfires = len(master_data) - num_fires
fire_pad = round(num_nonfires/num_fires)-1

for ind in fire_inds:
    fire_row = master_data[ind]
    for j in range(fire_pad):
        master_data.append(fire_row)
'''
