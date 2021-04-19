#importing libraries
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt #for. graphs
import pandas as pd #for matrices and data sets
#import seaborn as sns
#%matplotlib inline
import math
import requests as rs
import datetime
datetime.datetime.strptime
from datetime import datetime, timedelta
import warnings
import io
import urllib
import base64
warnings.filterwarnings('ignore')


def load_data():
    print("inside load data")
    csv_url = "https://docs.google.com/spreadsheets/d/1Cz0PV-_-kxQNSmSTcYM7ut35fqBBb4owdujFot0VDIg/export?format=csv&gid=0"
    res = rs.get(url=csv_url)
    open('covid19data.csv', 'wb').write(res.content)

    vacc_csv_url = "https://docs.google.com/spreadsheets/d/1Cz0PV-_-kxQNSmSTcYM7ut35fqBBb4owdujFot0VDIg/export?format=csv&gid=326396752"
    res_vacc = rs.get(url=vacc_csv_url)
    open('vaccinations.csv', 'wb').write(res_vacc.content)

    state_csv_url = "https://docs.google.com/spreadsheets/d/1Cz0PV-_-kxQNSmSTcYM7ut35fqBBb4owdujFot0VDIg/export?format=csv&gid=698347432"
    res_states = rs.get(url=state_csv_url)
    open('states.csv', 'wb').write(res_states.content)


def read_data():
    data = pd.read_csv("covid19data.csv")
    data['Date'] = data['Date'].astype('datetime64[ns]')
    #vacc_data = pd.read_csv("vaccinations.csv")
    #data['State'] = data['State'].astype('datetime64[ns]')
    return data

def read_vacc_data():
    vacc_data = pd.read_csv("vaccinations.csv")
    vacc_data['State'] = vacc_data['State'].astype('datetime64[ns]')
    return vacc_data

def cleanse_data():
    Data = read_data()
    #format date
    Data['Date'] = pd.to_datetime(Data['Date'], format='%Y%m%d')
    #correct Punjab's testing data before 2nd Apr 2020
    Data.loc[
        ((Data['Tested'] == 3675493.0) & (Data['State'] == 'PB') & (Data['Date'] < datetime(2020, 4, 2))), 'Tested'] = 0
    # Convert state data to string type
    Data['State'] = Data['State'].apply(str)
    # Adding some columns in data
    Data['Active'] = Data.apply(lambda row: (row['Confirmed'] - row['Recovered'] - row['Deceased']), axis=1)
    Data['Daily Confirmed'] = Data.groupby('State')['Confirmed'].apply(lambda x: x - x.shift(1)).fillna(0)
    Data['Daily Deceased'] = Data.groupby('State')['Deceased'].apply(lambda x: x - x.shift(1)).fillna(0)
    Data['Daily Recovered'] = Data.groupby('State')['Recovered'].apply(lambda x: x - x.shift(1)).fillna(0)
    Data['Daily Active'] = Data.apply(lambda row: (row['Daily Confirmed'] - row['Daily Recovered'] - row['Daily Deceased']), axis=1)
    Data['Daily Tested'] = Data.groupby('State')['Tested'].apply(lambda x: x - x.shift(1)).fillna(0)
    Data['Positivity Pct'] = Data.apply(lambda x: (x['Confirmed']/x['Tested'])*100 if x['Tested']!=0 else 0, axis=1)
    Data['Daily Positivity Pct'] = Data.apply(lambda x: (x['Daily Confirmed']/x['Daily Tested'])*100 if x['Daily Tested']!=0 else 0, axis=1)
    Data['7-dayMV Confirmed'] = Data.groupby('State')['Daily Confirmed'].apply(lambda x: x.rolling(7).mean())
    Data['7-dayMV Deceased'] = Data.groupby('State')['Daily Deceased'].apply(lambda x: x.rolling(7).mean())
    Data['7-dayMV Recovered'] = Data.groupby('State')['Daily Recovered'].apply(lambda x: x.rolling(7).mean())
    Data['7-dayMV Active'] = Data.groupby('State')['Daily Active'].apply(lambda x: x.rolling(7).mean())
    Data['7-dayMV Tested'] = Data.groupby('State')['Daily Tested'].apply(lambda x: x.rolling(7).mean())
    Data['7-dayMV Positivity Pct'] = Data.groupby('State')['Daily Positivity Pct'].apply(lambda x: x.rolling(7).mean())
    Data['TestingPerMillion'] = Data.apply(lambda x: (x['Tested']/x['Population'])*1000000 if x['Population']!=0 else 0, axis=1)
    Data['Daily TestingPerMillion'] = Data.apply(lambda x: (x['Daily Tested']/x['Population'])*1000000 if x['Population']!=0 else 0, axis=1)
    Data['7-dayMV TestingPerMillion'] = Data.groupby('State')['Daily TestingPerMillion'].apply(lambda x: x.rolling(7).mean())

    return Data


def show_plot(state,start_date,end_date,categories, type,typeOfChart):
    ax = plt.gca()
    data = cleanse_data()
    vacc_data = read_vacc_data();
    vacc_data.rename(columns={'Total': 'TT'}, inplace=True)
    vacc_data.rename(columns={'State': 'Date'}, inplace=True)
    vacc_data = vacc_data.filter(items=['Date',state])
    vacc_data['Lag'] = vacc_data[state].shift(1).fillna(0)
    vacc_data['Daily Vaccinations'] = vacc_data[state] - vacc_data['Lag']
    from_date=pd.Timestamp(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    to_date = pd.Timestamp(int(end_date.split("-")[0]), int(end_date.split("-")[1]),
                             int(end_date.split("-")[2]))
    filterMask = (data['State']==state) & (data['Date'] >= from_date) & (data['Date'] <= to_date)
    vaccMask = (vacc_data['Date'] >= from_date) & (vacc_data['Date'] <= to_date)
    data = data[filterMask]
    vacc_data = vacc_data[vaccMask]
    vacc_data.rename(columns={ vacc_data.columns[1]: "Vaccinations" }, inplace=True)

    merged_data = pd.merge(data, vacc_data, how='left', on=['Date'])
    #print(data.size)
    #data.plot(kind='line', x='Date', y=categories, ax=ax)
    type = '' if (type=='Cumulative') else type
    for item in categories:
        #plt.plot(data['Date'], data[item], label=item)
        merged_data.plot(kind=typeOfChart, x='Date', y=type+item, ax=ax)
    #handles, labels = plt.gca().get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #plt.legend(by_label.values(), by_label.keys())
    #plt.show()
    fig = plt.gcf()
    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri





def get_state_select():
    # importing data sets
    data = pd.read_csv("states.csv")
    #html = "<select name=\"state\" id=\"state\">";
    #for index, row in data.iterrows():
    #    html+="<option value=\""+row[1]+"\">"+row[0]+"</option>"
    #html+="</select>"
    arrStates = data.values
    #print(arrStates)
    arrStates = np.concatenate((arrStates,[['India','TT']]))
    #print(arrStates)
    return arrStates


def show_sc_plot(state1,state2,start_date,end_date,category, type,typeOfChart):
    type = '' if (type == 'Cumulative') else type
    field = type + category
    ax = plt.gca()
    data = cleanse_data()
    from_date=pd.Timestamp(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    to_date = pd.Timestamp(int(end_date.split("-")[0]), int(end_date.split("-")[1]),
                                 int(end_date.split("-")[2]))

    vacc_data = read_vacc_data();
    vacc_data.rename(columns={'Total': 'TT'}, inplace=True)
    vacc_data.rename(columns={'State': 'Date'}, inplace=True)
    vacc_data1 = vacc_data.filter(items=['Date',state1])
    vacc_data1['Lag'] = vacc_data1[state1].shift(1).fillna(0)
    vacc_data1['Daily Vaccinations'] = vacc_data1[state1] - vacc_data1['Lag']

    filterMask1 = (data['State']==state1) & (data['Date'] >= from_date) & (data['Date'] <= to_date)
    vaccMask = (vacc_data['Date'] >= from_date) & (vacc_data['Date'] <= to_date)
    data1 = data[filterMask1]
    vacc_data1 = vacc_data1[vaccMask]
    vacc_data1.rename(columns={ vacc_data1.columns[1]: "Vaccinations" }, inplace=True)
    merged_data1 = pd.merge(data1, vacc_data1, how='left', on=['Date'])
    merged_data1 = merged_data1.filter(items=['Date', field])

    vacc_data2 = vacc_data.filter(items=['Date', state2])
    vacc_data2['Lag'] = vacc_data2[state2].shift(1).fillna(0)
    vacc_data2['Daily Vaccinations'] = vacc_data2[state2] - vacc_data2['Lag']
    filterMask2 = (data['State'] == state2) & (data['Date'] >= from_date) & (data['Date'] <= to_date)
    #vaccMask = (vacc_data['Date'] >= from_date) & (vacc_data['Date'] <= to_date)
    data2 = data[filterMask2]
    vacc_data2 = vacc_data2[vaccMask]
    vacc_data2.rename(columns={vacc_data2.columns[1]: "Vaccinations"}, inplace=True)
    merged_data2 = pd.merge(data2, vacc_data2, how='left', on=['Date'])
    merged_data2 = merged_data2.filter(items=['Date', field])

    merged_data = pd.merge(merged_data1,merged_data2, on=['Date'])
    merged_data.rename(columns={merged_data.columns[1]: field+"_"+state1,merged_data.columns[2]: field+"_"+state2}, inplace=True)

    #print(data.size)
    #data.plot(kind='line', x='Date', y=categories, ax=ax)

    #for item in categories:
        #plt.plot(data['Date'], data[item], label=item)
    print(merged_data)
    merged_data.plot(kind=typeOfChart, x='Date', y=field+"_"+state1, ax=ax)
    merged_data.plot(kind=typeOfChart, x='Date', y=field + "_" + state2, ax=ax)
        #merged_data2.plot(kind='line', x='Date', y=type + item, ax=ax)
    #handles, labels = plt.gca().get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #plt.legend(by_label.values(), by_label.keys())
    #plt.show()
    fig = plt.gcf()
    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri


def show_t10_plot(end_date,category, type):
    ax = plt.gca()
    data = cleanse_data()
    to_date = pd.Timestamp(int(end_date.split("-")[0]), int(end_date.split("-")[1]),
                          int(end_date.split("-")[2]))
    vacc_data = read_vacc_data();

    vacc_data.rename(columns={'Total': 'TT'}, inplace=True)
    #vacc_data.rename(columns={'State': 'Date'}, inplace=True)
    vaccMask = (vacc_data['State'].dt.date.astype(str) == end_date)
    vacc_data = vacc_data[vaccMask].transpose();
    #vacc_data = vacc_data.filter(items=['Date',state])
    #vacc_data['Lag'] = vacc_data[state].shift(1).fillna(0)
    #vacc_data['Daily Vaccinations'] = vacc_data[state] - vacc_data['Lag']

    filterMask = (~data['State'].isin(['TT'])) & (data['Date'].dt.date.astype(str) == end_date)

    data = data[filterMask]
    vacc_data.reset_index(level=0, inplace=True)
    vacc_data.rename(columns={ vacc_data.columns[0]: "State",vacc_data.columns[1]: "Vaccinations" }, inplace=True)


    merged_data = pd.merge(data, vacc_data, how='left', on=['State'])
    merged_data['Vaccinations'] = merged_data['Vaccinations'].astype(float)

    print(merged_data)
    type = '' if (type == 'Cumulative') else type
    Max_n = merged_data.nlargest(10, type+category)
    #print(data.size)
    #data.plot(kind='line', x='Date', y=categories, ax=ax)

        #plt.plot(data['Date'], data[item], label=item)
    Max_n.plot(kind='bar', x='State', y=type+category, ax=ax)
    #handles, labels = plt.gca().get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #plt.legend(by_label.values(), by_label.keys())
    #plt.show()
    fig = plt.gcf()
    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return uri
