import pandas as pd
import numpy as np
import pickle
import re
import random
import string
import matplotlib.pyplot as plt
import seaborn as sns
import math
from scipy.spatial.distance import cdist
import pylab
import itertools
from itertools import permutations, repeat
from statistics import mean 
from math import radians, cos, sin, asin, sqrt

def lonlat_to_km(x_cors, y_cors, dist):
    x_min = x_cors[0]
    x_max = x_cors[-1]
    y_min = y_cors[0]
    y_max = y_cors[-1]

    lat_1km = np.average([j-i for i, j in zip(x_cors[:-1], x_cors[1:])]) * (1/dist)
    lon_1km = np.absolute(np.average([j-i for i, j in zip(y_cors[:-1], y_cors[1:])]) * (1/dist))

    return(lat_1km, lon_1km)

def number_of_combinations(first, second):    
    if first == second:
        return math.factorial(first)
    else:
        top = max(first,second)
        bot = top - min(first,second)
        
        return math.factorial(top) / math.factorial(bot)

def calculate_distance(df, comb):
    c0 = df[df['phone_id']==comb[0]]
    c1 = df[df['phone_id']==comb[1]]

    lon1, lat1, lon2, lat2 = map(radians, [c0['lon'], c0['lat'], c1['lon'], c1['lat']])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
    
    # return np.sqrt(np.square(float(c0['x'])-float(c1['x'])) + np.square(float(c0['y'])-float(c1['y'])))

def find_combinations(df, first, second):
    if len(first) <= len(second):
        a = first['phone_id']
        b = second['phone_id']                
    else:
        a = second['phone_id']
        b = first['phone_id']

    unique_comb = [list(zip(a, p)) for p in permutations(b)]

    dist_sums = []
    distances = dict()
    for i in range(0,len(unique_comb)):
        u = unique_comb[i]
        dist_sum = 0
        for j in range(0,len(u)):
            dist = calculate_distance(df, u[j])
            dist_sum += dist
            distances[u[j]] = dist
        dist_sums.append(dist_sum)

    best_comb = unique_comb[np.argmin(dist_sums)]
    
    result = []
    for comb in best_comb:
        if distances[comb] <= 5:
            result.append(comb)
            
    return result

def match_phones(df):
    final_comb = []
    times = list(df['timestamp'].unique())
    for i in range(0,len(times)-1):
        first = df[df['timestamp']==times[i]]
        second = df[df['timestamp']==times[i+1]]
        n = number_of_combinations(len(first), len(second))
        if n <= 6:
            final_comb += find_combinations(df, first, second)

    return final_comb

def id_generator(size):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])

def assign_new_ids(df, combinations):
    # with open ('pickles/'+unit+'.pickle', 'rb') as fp:
    #     combinations = pickle.load(fp)

    groups = []
    for t in combinations:
        for group in groups:
            if any(x in group for x in t):
                group.update(t)
                break
        else:
            groups.append(set(t))

    for group in groups:
        ind = df[df['phone_id'].isin(group)].index
        df.loc[ind,'phone_id'] = id_generator(10)

    return df

def main():
    print("Load data")
    df = pd.read_pickle('pickles/poacher_risks.pickle')
    df = df.sort_values(by='timestamp')
    df['month'] = df['timestamp'].map(lambda x: x.month)

    # y = latitude, x = longitude
    x_cors = [26.013530731201172, 26.06018829345703, 26.106700897216797, 26.153261184692383, 26.2000675201416, 26.246292114257812]
    y_cors = [-14.73619556427002, -14.779047012329102, -14.826595306396484, -14.873619079589844, -14.916463851928711, -14.962969779968262, -15.007390022277832]
    lat_1km, lon_1km = lonlat_to_km(x_cors, y_cors, 5)
    df['y'] = df['lat']/lat_1km
    df['x'] = df['lon']/lon_1km

    print("Match phones per month and save to a pickle.")
    for m in df['month'].unique():
        print(m)
        final_comb = match_phones(df[df['month']==m])

        with open('pickles/combination_'+str(m)+'.pickle', 'wb') as fp:
            pickle.dump(final_comb, fp)
    # for unit in range(3,10):
        df = assign_new_ids(df, final_comb)

    df = df[['timestamp', 'date', 'time', 'phone_id', 'lat', 'lon', 'tourist_dist_km', 'closest_tourist_unit', 'road_dist_km', 'precipitation', 'risk', 'km_to_HQ']]
    with open('pickles/tracked_phones.pickle', 'wb') as fp:
        pickle.dump(df, fp)

if __name__ == "__main__":
    main()


