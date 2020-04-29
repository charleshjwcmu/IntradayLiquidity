# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 16:45:11 2018

@author: e620927
"""

import datetime
import os
import pandas as pd
import numpy as np
import imp
#import sys
PRODUCTION_ENVRIONMENT = True

if PRODUCTION_ENVRIONMENT:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes-Production"
else:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"

os.chdir(code_dir)
import UpdateDatabase_Intraday_DB
imp.reload(UpdateDatabase_Intraday_DB)

#new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME"
column_name_transaction_amount = "TRANSACTION_AMOUNT"
column_name_transaction_type = "TRANSACTION_TYPE"
column_name_datamart = "SOURCEDATAMART"
column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"
column_name_net_transaction = "NET_TOTAL_AT_TRANSCATION_TIME"
column_name_running_total = "RUNNING_TOTAL"
column_name_15minutes = "Time15Minute"
column_name_30minutes = "Time30Minute"
column_name_60minutes = "Time60Minute"

def clean_number(string):
    return(float(str(string).replace(',','').replace('(','-').replace(')','')))

def format_hour(hour):
    if hour < 10:
        return('0' + str(hour))
    else:
        return(str(hour))
        
def create_unique_dirname(filename):
#    filename = plot_folder
    filename2 = filename
    k = 1
    while os.path.exists(filename2):
        filename2 = filename + "_Update"+str(k)
        k = k+1
    return(filename2)

def extract_lnncp(running_tmp):
    if all(np.isnan(running_tmp)):
        return(np.nan)
    lnncp = min(running_tmp)
    return(lnncp)
def extract_lnncp_time(running_tmp):
    if all(np.isnan(running_tmp)):
        return(np.nan)
    lnncp = min(running_tmp)
    lnncp_time = running_tmp[running_tmp == lnncp].index[0]
    return(lnncp_time)
def extract_lpncp(running_tmp):
    if all(np.isnan(running_tmp)):
        return(np.nan)
    lpncp = max(running_tmp)
    return(lpncp)
def extract_lpncp_time(running_tmp):
    if all(np.isnan(running_tmp)):
        return(np.nan)
    lpncp = max(running_tmp)
    lpncp_time = running_tmp[running_tmp == lpncp].index[0]
    return(lpncp_time)

def process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(data_tmp, need_date = False):
    column_name_transaction_time = "TRANSACTION_DATE_TIME_GMT"
    column_name_transaction_amount = "DER_TRANSACTION_AMOUNT_USD"
    column_name_transaction_type = "TRANSACTION_TYPE"
    column_name_transaction_amount_local = "TRANSACTION_AMOUNT"

#    column_name_account_type = "ACCOUNT_TYPE"
#    column_name_agent_bank_name = "AGENT_BANK_NAME"
    column_name_market_account = "IBS_NOSTRO_NAME"
    column_name_currency = "CURRENCY_CODE"
    column_name_entity = "MATERIAL_ENTITY"

#    data_tmp = table_tmp.copy()
    if need_date:
        if data_tmp[column_name_transaction_time].iloc[0].__class__ is str:
            data_tmp[column_name_transaction_time] = [datetime.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p') for x in data_tmp[column_name_transaction_time]]
    else:
        if data_tmp[column_name_transaction_time].iloc[0].__class__ is str:
            data_tmp[column_name_transaction_time] = [datetime.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p').time() for x in data_tmp[column_name_transaction_time]]
        else:
            data_tmp[column_name_transaction_time] = [x.time() for x in data_tmp[column_name_transaction_time]]

    data_tmp[column_name_transaction_amount] = data_tmp[column_name_transaction_amount].apply(clean_number)
    # enrich FMU 
    data_tmp["FMU"]="Excluded"
    
    #GBP
    data_tmp.loc[data_tmp[column_name_market_account].isin(["BOERESERVEGBP","OMNIGBPBOE"]),"FMU"] = "GBP_CHAPSandCREST"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["3793EURGBP"]),"FMU"] = "GBP_EB"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["SSBLDNGBP"]),"FMU"] = "GBP_RBS"
    data_tmp.loc[(data_tmp[column_name_currency].isin(["GBP"])) & (~ data_tmp[column_name_market_account].isin(["BOERESERVEGBP","OMNIGBPBOE","3793EURGBP","SSBLDNGBP"])),"FMU"] = "GBP_OTHERS"

    #CAD
    data_tmp.loc[data_tmp[column_name_market_account].isin(["LVTSNOST1CAD"]),"FMU"] = "CAD_LVTS"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["CDSNOSTROCAD1"]),"FMU"] = "CAD_CDS"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["OMNICADFD"]),"FMU"] = "CAD_FD"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["CLSC3PNETCAD"]),"FMU"] = "CAD_CLS"
    data_tmp.loc[(data_tmp[column_name_currency].isin(["CAD"])) & (~ data_tmp[column_name_market_account].isin(["LVTSNOST1CAD","CDSNOSTROCAD1","OMNICADFD","CLSC3PNETCAD"])),"FMU"] = "CAD_OTHERS"

    #JPY
    data_tmp.loc[data_tmp[column_name_market_account].isin(["OMNIJPYFUJI"]),"FMU"] = "JPY_Mizuho"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["OMNIJPYHSBC"]),"FMU"] = "JPY_HSBC"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["NOSTJPY01","NOSTJPY02","JPYNOSTRO","JPYFXC"]),"FMU"] = "JPY_BTMU"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["CLSC3PNETJPY"]),"FMU"] = "JPY_CLS"
    data_tmp.loc[(data_tmp[column_name_currency].isin(["JPY"])) & (~ data_tmp[column_name_market_account].isin(["OMNIJPYFUJI","OMNIJPYHSBC","NOSTJPY01","NOSTJPY02","JPYNOSTRO","JPYFXC","CLSC3PNETJPY"])),"FMU"] = "JPY_OTHERS"

    #EUR
    data_tmp.loc[data_tmp[column_name_market_account].isin(["PRIMARYEUR"]),"FMU"] = "EUR_London_DB"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["3793EURO","EUFEUR"]),"FMU"] = "EUR_London_Euroclear"

    data_tmp.loc[data_tmp[column_name_market_account].isin(["NOSTEUR02"]),"FMU"] = "EUR_GmbH_DB"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["NOSTCHQEUR01","NOSTCHQITEUR01","NOSTEUR01","NOSTSCTEUR01","NOSTSDDEUR01","NOSTUCHEUR01"]),"FMU"] = "EUR_GmbH_ISP"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["BOERESERVEEUR","NOSTDNBEUR01","TGTEUR01","NOSTCBFEUR01"]),"FMU"] = "EUR_Target2_Combined"
    accounts = ["PRIMARYEUR","3793EURO","EUFEUR","NOSTEUR02","NOSTCHQEUR01","NOSTCHQITEUR01","NOSTEUR01","NOSTSCTEUR01","NOSTSDDEUR01","NOSTUCHEUR01","BOERESERVEEUR","NOSTDNBEUR01","TGTEUR01","NOSTCBFEUR01"]
    data_tmp.loc[(data_tmp[column_name_currency].isin(["EUR"])) & data_tmp[column_name_entity].isin(["SSB&T - London"]) & (~ data_tmp[column_name_market_account].isin(accounts)),"FMU"] = "EUR_London_OTHERS"
    data_tmp.loc[(data_tmp[column_name_currency].isin(["EUR"])) & data_tmp[column_name_entity].isin(["SSB GmbH"]) & (~ data_tmp[column_name_market_account].isin(accounts)),"FMU"] = "EUR_GmbH_OTHERS"
    
    # adjust amounts
    data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount] = data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount]*-1
    data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount_local] = data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount_local]*-1

    data_tmp.index = data_tmp[column_name_transaction_time]
    data_tmp = data_tmp.sort_index()
    
    data_tmp[column_name_hourminue] = [format_hour(x.hour) + ":" + format_hour(x.minute) for x in data_tmp.index]
    data_tmp[column_name_15minutes] = [format_hour(x.hour) + ":" + format_hour(15*(x.minute // 15)) for x in data_tmp.index]
    data_tmp[column_name_30minutes] = [format_hour(x.hour) + ":" + format_hour(30*(x.minute // 30)) for x in data_tmp.index]
    data_tmp[column_name_60minutes] = [format_hour(x.hour) + ":" + format_hour(60*(x.minute // 60)) for x in data_tmp.index]
    
    data_tmp.index.name = ""

    return(data_tmp)

def process_bcbs_extract_a1_report(data_tmp, need_date = False):
#    data_tmp = table_tmp.copy()
    if need_date:
        if data_tmp[column_name_transaction_time].iloc[0].__class__ is not pd._libs.tslib.Timestamp:
            data_tmp[column_name_transaction_time] = [datetime.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p') for x in data_tmp[column_name_transaction_time]]
    else:
        if data_tmp[column_name_transaction_time].iloc[0].__class__ is not pd._libs.tslib.Timestamp:
            data_tmp[column_name_transaction_time] = [datetime.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p').time() for x in data_tmp[column_name_transaction_time]]
        else:
            data_tmp[column_name_transaction_time] = [x.time() for x in data_tmp[column_name_transaction_time]]
            
    data_tmp = data_tmp[data_tmp["SOURCEDATAMART"]!="MTS_ABAL_TRANSACTION"]
    # enrich FMU 
    data_tmp["FMU"]=""
    data_tmp.loc[data_tmp["FED_CHIPS_BT"]=="CHIPS","FMU"] = "CHIPS"
    data_tmp.loc[data_tmp["FED_CHIPS_BT"]=="BT","FMU"] = "BOOK TRANSFER"
    data_tmp.loc[data_tmp["FED_CHIPS_BT"]=="FEDWR","FMU"] = "Fedwire Funds"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_FEDWIRE_CHIPS_TRANSACTION_FUNDING_CHIPS_SIDE") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "CHIPS"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_STS_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_CHK_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Funds"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_ACH_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Funds"
#    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_CHK_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "FED CHK"
#    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_ACH_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "FED ACH"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_FICC_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "DTCC - FICC"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_NSS_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Funds"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_EOD_DTC_SETTLEMENT_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Funds"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_ACAP_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_STS_TRANSACTION_REALTIME_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    
    data_tmp.loc[data_tmp["FMU"]=="CHIPS",'CLEARING_MATERIAL_ENTITY'] = "CHIPS"

    if any(data_tmp["FMU"]==""):
        print("Error: FMU has missing values! Check.")
#        data_tmp[data_tmp["FMU"]==""].to_excel(plot_folder+"/FMU_ERROR.xlsx")
    
    # enrich missing DDA with Fund number
    data_tmp[column_name_transaction_amount] = data_tmp[column_name_transaction_amount].apply(clean_number)
    
    if column_name_net_transaction in data_tmp.columns:
        data_tmp[column_name_net_transaction] = data_tmp[column_name_net_transaction].apply(clean_number)
    if column_name_running_total in data_tmp.columns:
        data_tmp[column_name_running_total] = data_tmp[column_name_running_total].apply(clean_number)

    data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount] = data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount]*-1

    data_tmp.loc[data_tmp[column_name_transaction_type] == "BOOK TRANSFER",column_name_transaction_amount] = 0

    data_tmp.index = data_tmp[column_name_transaction_time]
    data_tmp = data_tmp.sort_index()
#    if need_date:
#        data_tmp.index[0].strftime("%Y-%m-%d %H:%M:%S")
#        data_tmp['TimeBucket'] = [format_hour(x.hour) + " - " + format_hour(x.hour+1) for x in data_tmp.index]
#        data_tmp['TimeMinute'] = [format_hour(x.hour) + ":" + format_hour(x.minute) for x in data_tmp.index]
#    else:
    data_tmp[column_name_hour] = [format_hour(x.hour) + " - " + format_hour(x.hour+1) for x in data_tmp.index]
    data_tmp[column_name_hourminue] = [format_hour(x.hour) + ":" + format_hour(x.minute) for x in data_tmp.index]
    data_tmp[column_name_15minutes] = [format_hour(x.hour) + ":" + format_hour(15*(x.minute // 15)) for x in data_tmp.index]
    data_tmp[column_name_30minutes] = [format_hour(x.hour) + ":" + format_hour(30*(x.minute // 30)) for x in data_tmp.index]
    data_tmp[column_name_60minutes] = [format_hour(x.hour) + ":" + format_hour(60*(x.minute // 60)) for x in data_tmp.index]
#    data_tmp['Time30Minute'] = [datetime.time(x.hour,30*(x.minute // 30)) for x in data_tmp.index]

    if need_date:
        data_tmp['TimeInterval'] = [datetime.datetime(x.year, x.month, x.day, x.hour,15*(x.minute // 15)) for x in data_tmp.index]
    
    data_tmp.index.name = ""

    return(data_tmp)

