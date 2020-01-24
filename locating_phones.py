import pandas as pd
import numpy as np
import pickle
import re
import random
import string

# SQUARES
def four(df, ind):
    df.loc[ind,'phone_id'] = id_generator(10)
    x = round(df['x_cor_rssi'][ind].mean(),1)
    y = round(df['y_cor_rssi'][ind].mean(),1)
    
    for i in ind:
        df.loc[i,'phone_cor_x'] = x
        df.loc[i,'phone_cor_y'] = y

    return df        

def locate_squares(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    # try all detections, if there are multiple for the same beacon
    if all(b in beacons for b in [(y,x),(y,x+1),(y+1,x),(y+1,x+1)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y,x+1)].index:
                for C in df_empty[df_empty['name'] == (y+1,x)].index:
                    for D in df_empty[df_empty['name'] == (y+1,x+1)].index:
                        
                        # constraints for the phone being in the middle part of a square
                        if (df_empty.loc[[A,B,C,D]]['rssi'].sum() > (712-buffer)) and (df_empty.loc[[A,B,C,D]]['rssi'].sum() < (774+buffer)):
                            if min(df_empty.loc[[A,B,C,D]]['rssi']) > (106-buffer):
                                four(df, [A,B,C,D])
                                rm = set([A,B,C,D])
                                ind_new = [e for e in ind if e not in rm]
                                locate_squares(df, ind_new, x, y, buffer)
                                return
    else:
        if x < 5:
            x += 1
            locate_squares(df, ind, x, y, buffer)
        elif y < 6:
            x = 1
            y += 1
            locate_squares(df, ind, x, y, buffer)
        else:
            return

    return df 

# TRIANGLES
def three(df, ind, case):
    df.loc[ind,'phone_id'] = id_generator(10)
    side = round(np.sqrt((df.loc[ind[0]]['rssi']**2)/2),1)
    
    if case == 0:
        x = df.loc[ind[0]]['x_cor_rssi'] + side
        y = df.loc[ind[0]]['y_cor_rssi'] + side
    elif case == 1:
        x = df.loc[ind[0]]['x_cor_rssi'] - side
        y = df.loc[ind[0]]['y_cor_rssi'] + side
    elif case == 2:
        x = df.loc[ind[0]]['x_cor_rssi'] + side
        y = df.loc[ind[0]]['y_cor_rssi'] - side
    else:
        x = df.loc[ind[0]]['x_cor_rssi'] - side
        y = df.loc[ind[0]]['y_cor_rssi'] - side
        
    for i in ind:        
        df.loc[i,'phone_cor_x'] = x
        df.loc[i,'phone_cor_y'] = y

    return df        

def locate_triangles_0(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']

    beacons = list(df_empty['name'])
    
    if all(b in beacons for b in [(y,x),(y,x+1),(y+1,x)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y,x+1)].index:
                for C in df_empty[df_empty['name'] == (y+1,x)].index:
                    if (df_empty.loc[[A,B,C]]['rssi'].sum() > (496-buffer)) and (df_empty.loc[[A,B,C]]['rssi'].sum() < (519+buffer)):
                        if (df_empty.loc[A]['rssi'] < (132+buffer)) and (min(df_empty.loc[[B,C]]['rssi']) > (132-buffer)) and (max(df_empty.loc[[B,C]]['rssi']) < (255+buffer)):
                            three(df, [A,B,C],0)
                            rm = set([A,B,C])
                            ind_new = [e for e in ind if e not in rm]
                            locate_triangles_0(df, ind_new, x, y, buffer)
                            return
    else:
        if x < 5:
            x += 1
            locate_triangles_0(df, ind, x, y, buffer)
        elif y < 6:
            x = 1
            y += 1
            locate_triangles_0(df, ind, x, y, buffer)
        else:
            return
      
    return df

def locate_triangles_1(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    if all(b in beacons for b in [(y,x),(y,x-1),(y+1,x)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y,x-1)].index:
                for C in df_empty[df_empty['name'] == (y+1,x)].index:
                    if (df_empty.loc[[A,B,C]]['rssi'].sum() > (496-buffer)) and (df_empty.loc[[A,B,C]]['rssi'].sum() < (519+buffer)):
                        if (df_empty.loc[A]['rssi'] < (132+buffer)) and (min(df_empty.loc[[B,C]]['rssi']) > (132-buffer)) and (max(df_empty.loc[[B,C]]['rssi']) < (255+buffer)):
                            three(df, [A,B,C],1)
                            rm = set([A,B,C])
                            ind_new = [e for e in ind if e not in rm]
                            locate_triangles_1(df, ind_new, x, y, buffer)
                            return
    else:
        if x < 6:
            x += 1
            locate_triangles_1(df, ind, x, y, buffer)
        elif y < 6:
            x = 1
            y += 1
            locate_triangles_1(df, ind, x, y, buffer)
        else:
            return

    return df            

def locate_triangles_2(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    if all(b in beacons for b in [(y,x),(y-1,x),(y,x+1)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y-1,x)].index:
                for C in df_empty[df_empty['name'] == (y,x+1)].index:
                    if (df_empty.loc[[A,B,C]]['rssi'].sum() > (496-buffer)) and (df_empty.loc[[A,B,C]]['rssi'].sum() < (519+buffer)):
                        if (df_empty.loc[A]['rssi'] < (132+buffer)) and (min(df_empty.loc[[B,C]]['rssi']) > (132-buffer)) and (max(df_empty.loc[[B,C]]['rssi']) < (255+buffer)):
                            three(df, [A,B,C],2)
                            rm = set([A,B,C])
                            ind_new = [e for e in ind if e not in rm]
                            locate_triangles_2(df, ind_new, x, y, buffer)
                            return
    else:
        if x < 5:
            x += 1
            locate_triangles_2(df, ind, x, y, buffer)
        elif y < 7:
            x = 1
            y += 1
            locate_triangles_2(df, ind, x, y, buffer)
        else:
            return
    
    return df

def locate_triangles_3(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    if all(b in beacons for b in [(y,x),(y-1,x),(y,x-1)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y-1,x)].index:
                for C in df_empty[df_empty['name'] == (y,x-1)].index:
                    if (df_empty.loc[[A,B,C]]['rssi'].sum() > (496-buffer)) and (df_empty.loc[[A,B,C]]['rssi'].sum() < (519+buffer)):
                        if (df_empty.loc[A]['rssi'] < (132+buffer)) and (min(df_empty.loc[[B,C]]['rssi']) > (132-buffer)) and (max(df_empty.loc[[B,C]]['rssi']) < (255+buffer)):
                            three(df, [A,B,C],3)
                            rm = set([A,B,C])
                            ind_new = [e for e in ind if e not in rm]
                            locate_triangles_3(df, ind_new, x, y, buffer)
                            return
    else:
        if x < 6:
            x += 1
            locate_triangles_3(df, ind, x, y, buffer)
        elif y < 7:
            x = 1
            y += 1
            locate_triangles_3(df, ind, x, y, buffer)
        else:
            return

    return df

# BARS
def two(df, ind, case):
    df.loc[ind,'phone_id'] = id_generator(10)
    diff = (df.iloc[ind]['rssi'].sum() - 255)/2
    
    if case == 0:
        x = round(df.iloc[ind[0]]['x_cor_rssi'] + df.iloc[ind[0]]['rssi'] - diff,1)
        y = round(df.iloc[ind[0]]['y_cor_rssi'],1)
    else:
        x = round(df.iloc[ind[0]]['x_cor_rssi'],1)
        y = round(df.iloc[ind[0]]['y_cor_rssi'] + df.iloc[ind[0]]['rssi'] - diff,1)
    
    for i in ind:                               
        df.loc[i,'phone_cor_x'] = x
        df.loc[i,'phone_cor_y'] = y

    return df        

def locate_bars_0(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    if all(b in beacons for b in [(y,x),(y,x+1)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y,x+1)].index:
                if (df_empty.loc[[A,B]]['rssi'].sum() > (255-buffer)) and (df_empty.loc[[A,B]]['rssi'].sum() < (265+buffer)):
                    two(df, [A,B],0)
                    rm = set([A,B])
                    ind_new = [e for e in ind if e not in rm]
                    locate_bars_0(df, ind_new, x, y, buffer)
                    return
    else:
        if x < 5:
            x += 1
            locate_bars_0(df, ind, x, y, buffer)
        elif y < 7:
            x = 1
            y += 1
            locate_bars_0(df, ind, x, y, buffer)
        else:
            return
 
    return df

def locate_bars_1(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    if all(b in beacons for b in [(y,x),(y+1,x)]):
        for A in df_empty[df_empty['name'] == (y,x)].index:
            for B in df_empty[df_empty['name'] == (y+1,x)].index:
                if (df_empty.loc[[A,B]]['rssi'].sum() > (255-buffer)) and (df_empty.loc[[A,B]]['rssi'].sum() < (265+buffer)):
                    two(df, [A,B],1)
                    rm = set([A,B])
                    ind_new = [e for e in ind if e not in rm]
                    locate_bars_1(df, ind_new, x, y, buffer)
                    return
    else:
        if x < 6:
            x += 1
            locate_bars_1(df, ind, x, y, buffer)
        elif y < 6:
            x = 1
            y += 1
            locate_bars_1(df, ind, x, y, buffer)
        else:
            return

    return df

# DOTS
# for all datapoints that were the only ones detecting something, give a unique id and phone coordinate
def one(df, ind, buffer):
    for i in ind:
        df.loc[ind,'phone_id'] = id_generator(10)
        x = df['x_cor_rssi'][i]
        y = df['y_cor_rssi'][i]
        
        # if beacon is on the side
        if df['side'][i]:
            if df['x_name'][i] == 1:
                df.loc[i,'phone_cor_y'] = y
                df.loc[i,'phone_cor_x'] = x-df['rssi'][i]
            elif df['x_name'][i] == 6:
                df.loc[i,'phone_cor_y'] = y
                df.loc[i,'phone_cor_x'] = x+df['rssi'][i]
            elif df['y_name'][i] == 1:
                df.loc[i,'phone_cor_y'] = y-df['rssi'][i]
                df.loc[i,'phone_cor_x'] = x
            elif df['y_name'][i] == 7:
                df.loc[i,'phone_cor_y'] = y+df['rssi'][i]
                df.loc[i,'phone_cor_x'] = x
                
        # if beacon is in a corner
        elif df['corner'][i]:
            side = round(np.sqrt(df['rssi'][i])/2,1)
            if df['name'][i] == (1,1):
                df.loc[i,'phone_cor_y'] = y-side
                df.loc[i,'phone_cor_x'] = x-side
            elif df['name'][i] == (1,6):
                df.loc[i,'phone_cor_y'] = y-side
                df.loc[i,'phone_cor_x'] = x+side
            elif df['name'][i] == (7,1):
                df.loc[i,'phone_cor_y'] = y+side
                df.loc[i,'phone_cor_x'] = x-side
            elif df['name'][i] == (7,6):
                df.loc[i,'phone_cor_y'] = y+side
                df.loc[i,'phone_cor_x'] = x+side
                
        # if beacon is in the middle area
        else:
            if df['rssi'][i] < buffer:
                df.loc[i,'phone_cor_x'] = x
                df.loc[i,'phone_cor_y'] = y
            else:
                df.loc[i,'phone_cor_x'] = -1
                df.loc[i,'phone_cor_y'] = -1

    return df                

def locate_dots(df, ind, x, y, buffer):
    df_empty = df.loc[ind]
    df_empty = df_empty[df_empty['phone_id']=='']
    beacons = list(df_empty['name'])

    if (y,x) in beacons:
        for A in df_empty[df_empty['name'] == (y,x)].index:
            if any([df_empty.loc[A]['side'],df_empty.loc[A]['corner']]):
                one(df, [A], buffer)
                rm = set([A])
                ind_new = [e for e in ind if e not in rm]
                locate_dots(df, ind_new, x, y, buffer)
                return
        
            elif df_empty.loc[A]['rssi'].sum() < buffer:
                one(df, [A], buffer)
                rm = set([A])
                ind_new = [e for e in ind if e not in rm]
                locate_dots(df, ind_new, x, y, buffer)
                return
    else:
        if x < 6:
            x += 1
            locate_dots(df, ind, x, y, buffer)
        elif y < 7:
            x = 1
            y += 1
            locate_dots(df, ind, x, y, buffer)
        else:
            return

    return df            

def locate(df, t, buffer):
    indices = df[df['timestamp']==t].index.tolist()

    df = locate_squares(df, indices, 1, 1, buffer)
    
    df = locate_triangles_0(df, indices, 1, 1, buffer)
    df = locate_triangles_1(df, indices, 1, 2, buffer)
    df = locate_triangles_2(df, indices, 2, 1, buffer)
    df = locate_triangles_3(df, indices, 2, 2, buffer)
    
    df = locate_bars_0(df, indices, 1, 1, buffer)
    df = locate_bars_1(df, indices, 1, 1, buffer)
    
    df = locate_dots(df, indices, 1, 1, buffer)

    return df

def id_generator(size):
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)]) 

def set_phone_columns(df):
    df = df.drop(columns=['close'])
    df['phone_id'] = ''
    df['phone_cor_x'] = float
    df['phone_cor_y'] = float
    # df['found_len'] = df['found'].str.len()

    return df

def export_dataframe(df, timestamps, ts_start, ts_stop):
    i0 = df[df['timestamp']==timestamps[ts_start]].index.to_list()[0]
    i1 = df[df['timestamp']==timestamps[ts_stop]].index.to_list()[0]
    df = df.loc[i0:i1]

    if ts_start > 0:
        x = pd.read_pickle("pickles/df_phones.pickle")
        df = x.append(df, sort=False)

    pickle.dump(df, open("pickles/df_phones.pickle", "wb"))

def get_buffer(part):
    if part == 'A':
        return 25
    elif part == 'B':
        return 75
    elif part == 'C':
        return 150

def iterate(df, timestamps, i, steps, ts_stop, part):
    buffer = get_buffer(part)
    i1 = min(i+steps, ts_stop)
    for j in range(i, i1):
        print(j)
        df = locate(df, timestamps[j], buffer)
    return df