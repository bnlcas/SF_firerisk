import csv
import numpy
from scipy import stats
import math
import matplotlib.pyplot as plt
from sklearn.linear_model import Lasso
csv.field_size_limit(320000)


root_dir = '/Users/changlab/Documents/changrepo/matlab/analysis/Ishihara/Fire/Data/'
fire_data = 'Fire_Incidents.csv'
building_csv = 'LandUse2016.csv'
property_tax_csv = 'Historic_Secured_Property_Tax_Rolls.csv'



def get_element_ind(labels, tag):
    # Find the index where a given label occurs
    return [i for i in range(len(labels)) if labels[i] == tag][0]
    
def get_select_inds(list_data, inds):
    # down select data on the basis of a list of indecis
    return [item for i, item in enumerate(list_data) if i in inds]
    
def string2float(element, default):
    try:
        return float(element)
    except ValueError:
        return float(default)
        
  
    
#### Load Data:
data_table = []
with open(root_dir+fire_data, 'rb') as b:
    reader = csv.reader(b)
    for row in reader:
        data_table.append(row)

fire_headers = data_table[0]
fire_data = data_table[1:]

## Select only fire_data_pertinent to building fires
situation_col =  get_element_ind(fire_headers, 'Primary Situation')
# code 111 is for building fires:
building_fire_inds = [i for i, row in enumerate(fire_data) if '111' in row[situation_col]]
fire_data = get_select_inds(fire_data, building_fire_inds)




## Get data associted with the  location and damages:
address_ind = get_element_ind(fire_headers, 'Address')
magnitude_ind = get_element_ind(fire_headers, 'Suppression Personnel')

fire_address = [row[address_ind].split(' ')[0:2] for row in fire_data]
fire_magnitude = []
for row in fire_data:
    tmp = row[magnitude_ind]
    if tmp == '':
        fire_magnitude.append(0)
    else:
        fire_magnitude.append(math.log10(float(tmp)+1))





#building_data  = []
#OBJECTID 0 ,BLKLOT 1,the_geom 2,MAPBLKLOT 3,BLOCK_NU 4M,LOT_NU 5 M,FROM_ST,TO_ST 7 ,STREET 8,ST_TYPE 9 ,RESUNITS 10,BLDGSQFT 11,YRBUILT 12,TOTAL_USES 13,LANDUSE 14,
property_tax_data = []
building_latlong = []
with open(root_dir+ property_tax_csv, 'rb') as b:
    reader = csv.reader(b)
    for dat in reader:
        building_latlong.append(dat[-1])
lot_num = ['lot_number']
for i in range(1,203054):
    lot_num.append([i])

out = zip(lot_num, building_latlong)
out_clipped = [];
for entry in out:
    if entry[1] != '':
        out_clipped.append(entry)
        
with open('building_coords.csv', 'wb') as f:
    writer = csv.writer(f,)
    writer.writerows(out_clipped)



building_data  = []

relevant_ind = range(7,15)
street_num = []
street_name = []
num_res_units = []
sq_ft = []
age = []
total_uses = []
main_use = []
i = 0
with open(root_dir+'LandUse2016.csv', 'rb') as b:
    reader = csv.reader(b)
    for dat in reader:
        dat = get_select_inds(dat, relevant_ind)
        street_name.append(dat[1])
        street_num.append(dat[0])
        num_res_units.append(dat[3])
        sq_ft.append(dat[4])
        age.append(dat[5])
        total_uses.append(dat[6])
        main_use.append(dat[7])



tmp = [string2float(x,1000) for x in age]
mean_age_good = np.asscalar(np.mean([x for x in tmp if x >= 1800 and x < 2017]))
age = [2016-mean_age_good if x <1800 or x > 2016 else 2016 - x for x in tmp]
age_count = zip(list(set(tmp)), [tmp.count(x) for x in list(set(tmp))])


num_res_units = [string2float(x, 0.0) for x in num_res_units]
sq_ft = [string2float(x, 1000.0) for x in sq_ft]
total_uses = [string2float(x,0) for x in total_uses]


## Make Dumy Vars for use type
use_types = list(set(main_use))
use_count = [main_use.count(use_type) for use_type in use_types]
use_tup = zip(use_types, use_count)
use_tup = sorted(use_tup, key = lambda x: x[1], reverse = True)
use_types_primary = use_tup[0:3]
use1 = [float(use_types_primary[0][0] in x) for x in main_use]
use2 = [float(use_types_primary[1][0] in x) for x in main_use]
use3 = [float(use_types_primary[2][0] in x) for x in main_use]

X_data = np.zeros((len(num_res_units),8))
for i in range(len(num_res_units)):
    X_data[i,0] = 1.0
    X_data[i,1] = num_res_units[i]
    X_data[i,2] = sq_ft[i]
    X_data[i,3] = age[i]
    X_data[i,4] = total_uses[i]
    X_data[i,5] = use1[i]
    X_data[i,6] = use2[i]
    X_data[i,7] = use3[i]

parameter_list = ['offes', 'number of residential units', 'square footage', 'age','total uses', 'use1', 'use2', 'use3']
#Get Y data:
Y = np.zeros((len(num_res_units),1))

fire_address = [x for x in fire_address if len(x) >=2]
for fire_ind, fire_loc in enumerate(fire_address):
    data_ind = [i for i, st_name in enumerate(street_name) if st_name.lower() == fire_loc[1].lower() and street_num[i].lower()  == fire_loc[0].lower()]
    if len(data_ind)>0:
        Y[data_ind[0]] = fire_magnitude[fire_ind]


clf_lasso = Lasso(alpha=0.1)
out = clf_lasso.fit(X_data,Y)




'''## Parcel by Date

## Parcel by zip_code

zip_count = [[z, zipcode_data.count(z)] for z in set(zipcode_data) if z != '']

## Fires per year:
year_data = [date.split('/')[2] for date in date_data]
month_data = [date.split('/')[0]+date.split('/')[2] for date in date_data]
month_only_data = [date.split('/')[0] for date in date_data]
fires_per_year = [year_data.count(y) for y in set(year_data) if y !='']
fires_per_month = [month_data.count(y) for y in set(month_data) if y !='']
fires_per_month_only = [month_only_data.count(y) for y in set(month_only_data) if y !='']

## Fano factor != 1
plt.hist(fires_per_month, 15, normed=0, facecolor='blue', alpha=0.75)
## month data does not show strong seasonality
plt.bar(range(1,13),fires_per_month_only)

## INCOME by zipcode:
income = [38077, 100114, 66607, 53150, 60230, 83542, 82993, 79407, 84488, 103472, 84828, 103333, 122970, 85330, 131108, 49594, 121200, 86070, 70220, 144886, 63173, 36875, 41612, 24127, 170656, 80341, 120610]
population = [2880, 26881, 28129, 26237, 40798, 4792, 38319, 79407, 69333, 3713, 43698, 39169, 31124, 33021, 19289, 33996, 23088, 56023, 41203, 3183, 55984, 13768, 27170, 31176, 5846, 406, 26599]

tmp =  [y[1] for y in zip_count]
fires_per_year_per_capital = [float(tmp[i])/float(population[i]) for i in range(len(population))]

stats.pearsonr(tmp, income)
# R is - .37

stats.pearsonr(fires_per_year_per_capital, income)
# R is -0.17'''
