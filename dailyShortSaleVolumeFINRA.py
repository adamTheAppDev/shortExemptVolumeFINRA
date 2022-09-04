# -*- coding: utf-8 -*-
"""
reg SHO Daily Short Sale Volume FINRA
@author: adam getbags
"""

# import modules
import pandas as pd
import requests
import yahoo_fin.stock_info as si
from datetime import timedelta

# assign dataset to request
groupName = 'otcmarket'
datasetName = 'regShoDaily'

# assign ticker
ticker = 'BBBY'

# build URL
url = f'https://api.finra.org/data/group/{groupName}/name/{datasetName}'

# create headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    }

# create custom filter
customFilter = {
    "limit" : 5000,
    "compareFilters": [
        {"compareType": "equal", 
          "fieldName": "securitiesInformationProcessorSymbolIdentifier", 
          "fieldValue" : "BBBY"}
    ]
    }

# make POST request
request = requests.post(url, headers=headers, json=customFilter)

# format to dataframe
data = pd.DataFrame.from_dict(request.json())
# format date
data.tradeReportDate = pd.to_datetime(data.tradeReportDate)

# define aggregate functions to apply 
aggFunc = {'totalParQuantity' : 'sum',
    'shortParQuantity': 'sum', 
    'shortExemptParQuantity': 'sum'}

aggData = data.groupby(['tradeReportDate']).agg(aggFunc)
aggData.index.names = ['Date']
aggData.columns = ['volumeFINRA', 'shortVolumeFINRA', 'shortExemptVolumeFINRA']

# get dates for volume request
startDate = aggData.index[-1] - timedelta(days=365)
endDate = aggData.index[-1] + timedelta(days=1)

# request techincal data from Yahoo
technicalData = si.get_data('BBBY', start_date = startDate, 
                            end_date = endDate)

# add total volume column // integer formatting
aggData['totalVolume'] = technicalData['volume'].astype(int)

# short volume from FINRA over total volume from FINRA 
aggData['shortVolOverTVFINRA'] = aggData['shortVolumeFINRA'
                                        ]/aggData['volumeFINRA']

# short volume from FINRA over total volume 
aggData['shortVolOverTV'] = aggData['shortVolumeFINRA']/aggData['totalVolume']

# short exempt volume from FINRA over short volume from FINRA 
aggData['shortExemptVolOverSVFINRA'] = aggData['shortExemptVolumeFINRA'
                                              ] / aggData['shortVolumeFINRA']

# short exempt volume from FINRA over total volume from FINRA
aggData['shortExemptVolOverTVFINRA'] = aggData['shortExemptVolumeFINRA'
                                        ]/aggData['volumeFINRA']

# short exempt volume from FINRA over total volume 
aggData['shortExemptVolOverTV'] = aggData['shortExemptVolumeFINRA'
                                   ]/aggData['totalVolume']

# line charts
aggData['shortVolOverTVFINRA'].plot()
aggData['shortVolOverTV'].plot()
aggData['shortExemptVolOverSVFINRA'].plot()
aggData['shortExemptVolOverTVFINRA'].plot()
aggData['shortExemptVolOverTV'].plot()