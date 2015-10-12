import datetime
from dateutil import parser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import blpapi as blp
import seaborn as sns

SECURITY_DATA = blp.Name("securityData")
SECURITY = blp.Name("security")
FIELD_DATA = blp.Name("fieldData")
FIELD_EXCEPTIONS = blp.Name("fieldExceptions")
FIELD_ID = blp.Name("fieldId")
ERROR_INFO = blp.Name("errorInfo")

def blp_wrapper(secList, startDt, endDt, periodicitySelection='DAILY'):



    # Bloomberg API wrapper to retrieve Historical price data
    
    startDt = parser.parse(startDt).strftime('%Y%m%d')
    endDt   = parser.parse(endDt).strftime('%Y%m%d')
    periodicitySelection = periodicitySelection.upper()
    
    index = pd.date_range(startDt,endDt,freq='D')
    df_output = pd.DataFrame(index=index, columns=np.arange(len(secList)))
    df_output = df_output.fillna(np.NAN)
    
    # Connect to blp services
    sessionOptions = blp.SessionOptions()
    sessionOptions.setServerHost('localhost')
    sessionOptions.setServerPort(8194)

    # Open Bloomberg Session
    print "connecting to blp session..." 
    session = blp.Session(sessionOptions)
    if not session.start():
        print "...fail to connect!"
    else:
        print "...success!"
        
    # Open Bloomberg Session Service
    if not session.openService('//blp/refdata'):
        print 'Failed to open //blp/refdata'
    refDataService = session.getService('//blp/refdata')
    
    # Create Bloomberg request
    try:
        request = refDataService.createRequest('HistoricalDataRequest')
        for sec in secList:
            request.getElement('securities').appendValue(sec)
        request.getElement('fields').appendValue('PX_LAST')
        request.set('periodicityAdjustment', 'CALENDAR')
        request.set('periodicitySelection', periodicitySelection)
        request.set('startDate', startDt)
        request.set('endDate', endDt)
    except:
        print 'Error: Please check request parameters, request cannot be sent!'
        return

    print 'sending request...'

    session.sendRequest(request)

    print 'receiving request...'

    # Count the number of valid securities retrieved
    secCount = 0
    while(True):
        ev = session.nextEvent()
        for msg in ev:
            # Skip event msg that does not contain securiity data
            if not msg.hasElement('securityData'):
                continue

            secDataArray = msg.getElement(SECURITY_DATA)
            fieldData = secDataArray.getElement(FIELD_DATA)

            print secDataArray.getElementAsString(SECURITY), " has ", fieldData.numValues()

            # Rename column header to 'security name'
            df_output.rename(columns={secCount: secDataArray.getElementAsString(SECURITY)}, inplace=True)

            for i in range(0, fieldData.numValues()):
                field = fieldData.getValue(i)
                df_output.loc[field.getElement(0).getValue(), secDataArray.getElementAsString(SECURITY)] = field.getElement(1).getValue()

            secCount += 1
        
        # Exit Condition
        if ev.eventType() == blp.Event.RESPONSE:
            print '...all data have been received!'
            break 
    
    # Return system message and output
    print "# of securities retrieved: ", secCount
    session.stop()
    df_output.dropna(how='all', inplace=True)
    return df_output
    
