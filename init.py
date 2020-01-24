import pandas as pd
import pickle
import re
import uuid 

df = pd.read_csv('mock-data-180-days.csv')

df['timestamp'] = pd.to_datetime(df['timestamp'],unit='s')
df['coordinate'] = df['coordinate'].str.replace(';',',').str.replace(r'^','(').str.replace(r'$',')')

df = pd.concat([df,pd.DataFrame(df['coordinate'].str.split(",",expand=True,n=1))],axis=1)
df = df.rename(columns={0:'y_cor',1:'x_cor'}) 

df['x_cor'] = pd.to_numeric(df['x_cor'],downcast='float')
df['y_cor'] = pd.to_numeric(df['y_cor'],downcast='float')

# y groter: zuidelijker, y kleiner: noordelijker
# x groter: oostelijker, x kleiner: westelijker

x = list(df['x_cor'].unique())
x.sort()

x_dict = {
    26.013530731201172:1,
    26.06018829345703:2,
    26.106700897216797:3,
    26.153261184692383:4,
    26.2000675201416:5,
    26.246292114257812:6}

y = list(df['y_cor'].unique())
y.sort()

y_dict = {
    -15.007390022277832:7,
    -14.962969779968262:6,
    -14.916463851928711:5,
    -14.873619079589844:4,
    -14.826595306396484:3,
    -14.779047012329102:2,
    -14.73619556427002:1}


# #### Add 'det_name', 'x_name' and 'y_name' to the df, containing detector names

det_names_lst = list()
name_x_lst = list()
name_y_lst = list()
cor_lst = list()
for i in range(0,len(df)):
    x_cor = df['x_cor'][i]
    y_cor = df['y_cor'][i]
    cor_lst.append((y_cor,x_cor))
    
    x_name = x_dict[x_cor]
    y_name = y_dict[y_cor]
    
    name = (y_name,x_name)
    det_names_lst.append(name)
    name_x_lst.append(x_name)
    name_y_lst.append(y_name)
    
df['name'] = det_names_lst
df['x_name'] = name_x_lst
df['y_name'] = name_y_lst
df['coordinate'] = cor_lst


# #### Add 'side' and 'corner' to the df, containing whether detector is on the side or at the corner of the grid

# In[8]:


side_lst = list()
corner_lst = list()
for i in range(0,len(df)):
    x = df['x_name'][i]
    y = df['y_name'][i]
    
    side = False
    corner = False
    if(x==1 or x==6):
        if(y==1 or y==7):
            corner = True
        else:
            side = True
    elif(y==1 or y==7):
        side = True
    
    side_lst.append(side)
    corner_lst.append(corner)
    
df['side'] = side_lst
df['corner'] = corner_lst



close_lst = list()
for i in range(0,len(df)):
    x = df['x_name'][i]
    y = df['y_name'][i]
    cor = df['name'][i]
    
    close = dict()
    
    if df['corner'][i]:
        if cor==(1,1):
            close['R'] = (y,x+1)
            close['B'] = (y+1,x)
            close['BR'] = (y+1,x+1)
        elif cor==(7,1):
            close['R'] = (y,x+1)
            close['T'] = (y-1,x)
            close['TR'] = (y-1,x+1)
        elif cor==(1,6):
            close['L'] = (y,x-1)
            close['B'] = (y+1,x)
            close['BL'] = (y+1,x-1)
        elif cor==(7,6):
            close['L'] = (y,x-1)
            close['T'] = (y-1,x)
            close['TL'] = (y-1,x-1)
    elif df['side'][i]:
        if (x==1 or x==6):
            close['T'] = (y-1,x)
            close['B'] = (y+1,x)
            if x==1:
                close['R'] = (y,x+1)
                close['TR'] = (y-1,x+1)
                close['BR'] = (y+1,x+1)
            else:
                close['L'] = (y,x-1)
                close['TL'] = (y-1,x-1)
                close['BL'] = (y+1,x-1)
        if (y==1 or y==7):
            close['L'] = (y,x-1)
            close['R'] = (y,x+1)
            if y==1:
                close['B'] = (y+1,x)
                close['BL'] = (y+1,x-1)
                close['BR'] = (y+1,x+1)
            else:
                close['T'] = (y-1,x)
                close['TL'] = (y-1,x-1)
                close['TR'] = (y-1,x+1)
    else:
        close['B'] = (y+1,x)
        close['T'] = (y-1,x)
        close['L'] = (y,x-1)
        close['R'] = (y,x+1)
        close['TL'] = (y-1,x-1)
        close['BL'] = (y+1,x-1)
        close['TR'] = (y-1,x+1)
        close['BR'] = (y+1,x+1)
        
    close_lst.append(close)
    
df['close'] = close_lst


df = df[['timestamp','coordinate','x_cor','y_cor','name','x_name','y_name','side','corner','rssi','close']]


found_lst = list()
timestamps = list(df['timestamp'].unique())
for t in timestamps:
    df_time = df[df['timestamp'] == t]    
    indices = df_time.index.tolist()
    names = list(df_time['name'].unique())
    for i in indices:
        found = set()
        close = df_time['close'][i]
        for c in close:
            if close[c] in names:
                found.add(c)
        found_lst.append(found)

df['found'] = found_lst
df['x_cor_rssi'] = (df['x_name']*255)-255
df['y_cor_rssi'] = (df['y_name']*255)-255

pickle.dump(df, open("pickles/df_init.pickle", "wb"))