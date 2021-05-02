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
import os
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
    vacc_data = read_vacc_data()
    vacc_data.rename(columns={'Total': 'TT'}, inplace=True)
    vacc_data.rename(columns={'State': 'Date'}, inplace=True)
    vacc_data_unpivoted = vacc_data.melt(id_vars=['Date'], var_name='State', value_name='Vaccinations')
    vacc_data_unpivoted['Daily Vaccinations'] = vacc_data_unpivoted.groupby('State')['Vaccinations'].apply(lambda x: x - x.shift(1)).fillna(0)
    vacc_data_unpivoted['7-dayMV Vaccinations'] = vacc_data_unpivoted.groupby('State')['Daily Vaccinations'].apply(lambda x: x.rolling(7).mean())
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

    merged_data = pd.merge(Data, vacc_data_unpivoted, how='left', on=['Date','State'])

    return merged_data


def show_plot(state,start_date,end_date,categories, type,typeOfChart):
    ax = plt.gca()
    data = cleanse_data()
    #vacc_data['7-dayMV Vaccinations'] = vacc_data['Daily Vaccinations'].apply(lambda x: x.rolling(7).mean())
    from_date=pd.Timestamp(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    to_date = pd.Timestamp(int(end_date.split("-")[0]), int(end_date.split("-")[1]),
                             int(end_date.split("-")[2]))
    filterMask = (data['State']==state) & (data['Date'] >= from_date) & (data['Date'] <= to_date)
    data = data[filterMask]

    if(data.size==0):
        file = (os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/nodata.png'))
        with open(file, "rb") as image_file:
            data = base64.b64encode(image_file.read())
        uri = urllib.parse.quote(data)
        return uri
    #print(data.size)
    #data.plot(kind='line', x='Date', y=categories, ax=ax)
    type = '' if (type=='Cumulative') else type
    for item in categories:
        #plt.plot(data['Date'], data[item], label=item)
        data.plot(kind=typeOfChart, x='Date', y=type+item, ax=ax)
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



    filterMask1 = (data['State']==state1) & (data['Date'] >= from_date) & (data['Date'] <= to_date)
    data1 = data[filterMask1]


    filterMask2 = (data['State'] == state2) & (data['Date'] >= from_date) & (data['Date'] <= to_date)
    #vaccMask = (vacc_data['Date'] >= from_date) & (vacc_data['Date'] <= to_date)
    data2 = data[filterMask2]

    if (data1.size == 0 & data2.size ==0):
        file = (os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/nodata.png'))
        with open(file, "rb") as image_file:
            data = base64.b64encode(image_file.read())
        uri = urllib.parse.quote(data)
        return uri

    merged_data = pd.merge(data1,data2, on=['Date'])
    merged_data = merged_data[['Date',field+"_x",field+"_y"]]
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

    filterMask = (~data['State'].isin(['TT'])) & (data['Date'].dt.date.astype(str) == end_date)

    data = data[filterMask]


    type = '' if (type == 'Cumulative') else type
    Max_n = data.nlargest(10, type+category)
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

def show_misc_plots():
    data = cleanse_data()
    res = {}

    State_Total = data[data['State'].isin(['TT'])]
    maximums = State_Total.Date.max()
    mask = (State_Total.Date == maximums)
    State_Total = State_Total.loc[mask]

    State_Total1 = State_Total[["Recovered", "Deceased", "Active"]]
    mylabels = ["Recovered", "Deceased", "Active"]
    myexplode = [0, 0, 0.1]
    plt.pie(State_Total1.values[0], labels = mylabels,explode= myexplode,autopct='%1.1f%%')
    plt.title('Covid-19 situation in India so far (as of '+maximums.strftime("%m/%d/%Y")+')',fontweight="bold")
    plt.axis('equal')
    fig = plt.gcf()
    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    res['uri1'] = uri

    State_Total2 = State_Total[['Date','Population','Confirmed','Recovered','Deceased','Tested','Active','Positivity Pct','TestingPerMillion','Vaccinations']]
    State_Total2 = State_Total2.melt(id_vars=['Date'], var_name='Category', value_name='Value')
    State_Total2 = State_Total2[['Category','Value']]
    State_Total2.update(State_Total2[['Value']].applymap('{:,.1f}'.format))
    fig, ax = plt.subplots(1, 1)
    #column_labels = ["Category", "Value"]
    #df = pd.DataFrame(data, columns=column_labels)
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=State_Total2.values, colLabels=State_Total2.columns, colColours =["palegreen"] * 10, loc="center")
    ax.set_title('Covid-19 situation in India so far (as of '+maximums.strftime("%m/%d/%Y")+') - Table format',
                 fontweight="bold")
    table.set_fontsize(12)
    table.scale(1, 2)

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    res['uri2'] = uri
    return res

def my_fmt(x):
    print(x)
    return '{:.4f}%\n({:.0f})'.format(x, total*x/100)