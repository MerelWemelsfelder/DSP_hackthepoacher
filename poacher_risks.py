import pandas as pd
import numpy as np
import pickle
import re
import random
import string
import math
from scipy.spatial.distance import cdist

def find_closest_point(df, df_disruptions, name):
    df['closest_'+name+'_loc'] = [closest_point(x, list(df_disruptions['point'])) for x in df['point']]
    df['closest_'+name+'_unit'] = ''

    for i in range(0,len(df_disruptions)):
        print(df_disruptions['name'][i])
        dy = df_disruptions['y'][i]
        dx = df_disruptions['x'][i]

        point = df_disruptions['point'][i]
        indices = list(df[df['closest_'+name+'_loc']==point].index)

        df.loc[indices,  'closest_'+name+'_unit'] = df_disruptions['name'][i]
        df.loc[indices, name+'_dist_km'] = np.sqrt(np.square(df.loc[indices]['x']-dx) + np.square(df.loc[indices]['y']-dy))     
    
    return df

def dist_to_line(dx1, dy1, dx2, dy2, px, py):
    return np.absolute(((dy2-dy1)*px) - ((dx2-dx1)*py) + (dx2*dy1) - (dy2*dx1))/(np.sqrt(np.square(dy2-dy1) + np.square(dx2-dx1)))

def find_closest_line(df, df_disruptions, name, lat_1km, lon_1km):
    df = find_closest_point(df, df_disruptions, name)

    for i in range(1,len(df_disruptions)-1):
        dy0 = df_disruptions['y'][i-1]
        dx0 = df_disruptions['x'][i-1]
        dy1 = df_disruptions['y'][i]
        dx1 = df_disruptions['x'][i]
        dy2 = df_disruptions['y'][i+1]
        dx2 = df_disruptions['x'][i+1]

        name_unit = df_disruptions['name'][i]
        indices = list(df[df['closest_'+name+'_unit']==name_unit].index)

        px = df.loc[indices, 'x']
        py = df.loc[indices, 'y']
        df.loc[indices, 'dist_'+name+'_1'] = dist_to_line(dx0, dy0, dx1, dy1, px, py)
        df.loc[indices, 'dist_'+name+'_2'] = dist_to_line(dx1, dy1, dx2, dy2, px, py)
        df[name+'_dist_km'] = df[['dist_'+name+'_1','dist_'+name+'_2']].min(axis=1)
        
    return df

def lonlat_to_km(x_cors, y_cors, dist):
    x_min = x_cors[0]
    x_max = x_cors[-1]
    y_min = y_cors[0]
    y_max = y_cors[-1]

    lat_1km = np.average([j-i for i, j in zip(x_cors[:-1], x_cors[1:])]) * (1/dist)
    lon_1km = np.absolute(np.average([j-i for i, j in zip(y_cors[:-1], y_cors[1:])]) * (1/dist))

    return(lat_1km, lon_1km)

def closest_point(point, points):
    return points[cdist([point], points).argmin()]

def include_weather(df):
    weather = pd.read_csv('weather.csv')
    weather['date'] = pd.Series('2019/'+weather['month'].map(lambda x: str(x))+'/'+weather['day'].map(lambda x: str(x)))
    dates = pd.DataFrame(df['date'].unique())
    dates.columns = ['date']
    weather = dates.merge(weather, how='outer')

    weather = weather.fillna(-0.5)
    for i in range(0,len(weather)):
        if weather.loc[i, 'temp_max'] == -0.5:
            for column in ['temp_max','temp_avg','temp_min','precipitation']:
                base = weather.loc[i-1, column]
                weather.loc[i, column] = max(random.uniform(base-1.0, base+2.0), 0.0)

    normal_precipitation = pd.read_csv('normal_precipitation.csv').rename(columns={'precipitation':'precipitation_norm'})
    weather = pd.merge(weather, normal_precipitation, on='month')

    df = pd.merge(df, weather, on='date')
    return df

def risk_by_distance(df, disruptions, risk_max_dist, risk_impact):
    for d in disruptions:
        risk_diff = (df[d+'_dist_km']/risk_max_dist[d]) * risk_impact[d]
        risk_diff = risk_diff.map(lambda x: risk_impact[d] - round(min(x,risk_impact[d]),1))
        df['risk'] = df['risk'] - risk_diff

        df['risk'] = df['risk'].map(lambda x: max(0,x)).map(lambda x: min(100,x))
        
    return df

def risk_by_environment(df, d, risk_impact):
    nonzero = df[df[d+'_norm'] != 0].index
    zero = df[df[d+'_norm'] == 0].index

    risk_diff1 = ((df.loc[nonzero, d] - df.loc[nonzero, d+'_norm']) / df.loc[nonzero, d+'_norm']) * risk_impact[d]
    risk_diff1 = risk_diff1.map(lambda x: min(x, risk_impact[d])).map(lambda x: max(x, -risk_impact[d]))
    risk_diff2 = ((df.loc[zero, d] / (42.4/12)) * risk_impact[d]).map(lambda x: min(x, risk_impact[d]))

    df.loc[nonzero, 'risk'] = df.loc[nonzero, 'risk'] + risk_diff1
    df.loc[zero, 'risk'] = df.loc[zero, 'risk'] + risk_diff2

    df['risk'] = df['risk'].map(lambda x: max(0,x)).map(lambda x: min(100,x))

    return df

def main():
    df = pd.read_pickle('pickles/phones_located.pickle')
    df = df.rename(columns={'phone_lat':'lat', 'phone_lon':'lon'})
    df['point'] = [(x, y) for x,y in zip(df['lat'], df['lon'])]

    disturbances = pd.read_csv('disturbances.csv')
    disturbances['point'] = [(x, y) for x,y in zip(disturbances['lat'], disturbances['lon'])]

    df = include_weather(df)

    x_cors = [26.013530731201172, 26.06018829345703, 26.106700897216797, 26.153261184692383, 26.2000675201416, 26.246292114257812]
    y_cors = [-14.73619556427002, -14.779047012329102, -14.826595306396484, -14.873619079589844, -14.916463851928711, -14.962969779968262, -15.007390022277832]
    lat_1km, lon_1km = lonlat_to_km(x_cors, y_cors, 5)
    df['y'] = df['lat']/lat_1km
    df['x'] = df['lon']/lon_1km
    disturbances['y'] = disturbances['lat']/lat_1km
    disturbances['x'] = disturbances['lon']/lon_1km

    df_tourist = disturbances[disturbances['type']=='tourist lodge'].reset_index().drop(columns=['index'])
    df_road = disturbances[disturbances['type']=='road'].reset_index().drop(columns=['index'])

    # df = df[df['date']=='2019/3/23']
    print("Finding minimal distances to tourist lodge.")
    df = find_closest_point(df, df_tourist, 'tourist')
    print("Finding minimal distances to highway.")
    df = find_closest_line(df, df_road, 'road', lat_1km, lon_1km)
    print("Finding distance to head quarters.")
    df['km_to_HQ'] = np.sqrt(np.square(df['x']-(25.9255886/lon_1km)) + np.square(df['y']+(14.929449/lat_1km))) 

    risk_max_dist = {
    'tourist':4,
    'road':2
    }

    risk_impact = {
        'tourist':50,
        'road':50,
        'precipitation':20
    }

    df['risk'] = 50
    print("Calculating risks of being a poacher.")
    df = risk_by_distance(df, ['tourist', 'road'], risk_max_dist, risk_impact)
    df = risk_by_environment(df, 'precipitation', risk_impact)

    df = df[['timestamp', 'date', 'time', 'phone_id', 'lat', 'lon', 'tourist_dist_km', 'closest_tourist_unit', 'road_dist_km', 'precipitation', 'risk', 'km_to_HQ']]

    pickle.dump(df, open("pickles/poacher_risks.pickle", "wb"))

if __name__ == "__main__":
    main()