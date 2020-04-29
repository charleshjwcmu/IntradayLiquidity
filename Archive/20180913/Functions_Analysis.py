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
#    column_name_account_type = "ACCOUNT_TYPE"
#    column_name_agent_bank_name = "AGENT_BANK_NAME"
    column_name_market_account = "IBS_NOSTRO_NAME"
#    column_name_currency = "CURRENCY_CODE"
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
    
    data_tmp.loc[data_tmp[column_name_market_account].isin(["BOERESERVEGBP","OMNIGBPBOE"]),"FMU"] = "GBP_CHAPSandCREST"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["OMNICADFD"]),"FMU"] = "CAD_FD"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["CDSNOSTROCAD1","RBCNOSTROCAD1"]),"FMU"] = "CAD_RBC"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["PRIMARYEUR"]),"FMU"] = "EUR_DB_London"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["3793EURO"]),"FMU"] = "EUR_Euroclear_London"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["NOSTEUR02"]),"FMU"] = "EUR_DB_GmbH"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["NOSTEUR01"]),"FMU"] = "EUR_ISP_GmbH"
    
#    data_tmp.loc[data_tmp[column_name_market_account].isin(["JPYNOSTRO"]),"FMU"] = "JPY_BTMU_HK"
#    data_tmp.loc[data_tmp[column_name_market_account].isin(["JPYFXC"]),"FMU"] = "JPY_BTMU_Tokyo"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["JPYNOSTRO","JPYFXC"]),"FMU"] = "JPY_BTMU_Combined"

#    data_tmp.loc[data_tmp[column_name_market_account].isin(["LVTSNOST1CAD"]),"FMU"] = "CAD_LVTS"
#    data_tmp.loc[data_tmp[column_name_market_account].isin(["CDSNOSTROCAD1"]),"FMU"] = "CAD_CDS"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["LVTSNOST1CAD","CDSNOSTROCAD1"]),"FMU"] = "CAD_LVTS_CDS"

#    data_tmp.loc[data_tmp[column_name_market_account].isin(["BOERESERVEEUR"]),"FMU"] = "EUR_Target2_London"
#    data_tmp.loc[data_tmp[column_name_market_account].isin(["NOSTDNBEUR01","TGTEUR01","NOSTCBFEUR01"]),"FMU"] = "EUR_Target2_GmbH"
    data_tmp.loc[data_tmp[column_name_market_account].isin(["BOERESERVEEUR","NOSTDNBEUR01","TGTEUR01","NOSTCBFEUR01"]),"FMU"] = "EUR_Target2_Combined"

#    agent_bank_names = data_tmp[column_name_agent_bank_name].drop_duplicates()
#    def search_agent_bank(list_banks,agent_bank):
##        agent_bank = 'Direct Participation - Bank Of Canada'
##        list_banks = agent_bank_names
#        search_result = [x for x in list_banks if str(x).startswith(agent_bank)]
#        if len(search_result) == 1:
#            return(search_result[0])
#        elif len(search_result) == 0:
#            return("Not Found")
#        elif len(search_result) > 1:
#            sys.exit(search_result)            
#
#    # JPY
#    jpy_bank = search_agent_bank(agent_bank_names,'BANK OF TOKYO-MITSUBISHI UFJ')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == jpy_bank)&(data_tmp[column_name_account_type] == "PRI")&(data_tmp[column_name_currency] == "JPY")
#    data_tmp.loc[tmp_select,"FMU"] = "JPY-BTMU-PRI"
#
#    tmp_select = (data_tmp[column_name_agent_bank_name] == jpy_bank)&(data_tmp[column_name_account_type] == "CLS")&(data_tmp[column_name_currency] == "JPY")
#    data_tmp.loc[tmp_select,"FMU"] = "JPY-BTMU-CLS"
#
#    mizuho_bank = search_agent_bank(agent_bank_names,'MIZUHO BANK')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == mizuho_bank)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "JPY")
#    data_tmp.loc[tmp_select,"FMU"] = "JPY-MIZUHO-SEC"
#    
#    hsbc_bank = search_agent_bank(agent_bank_names,'HONGKONG AND SHANGHAI BANKING CORPORATION LIMITED,THE, TOKYO')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == hsbc_bank)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "JPY")
#    data_tmp.loc[tmp_select,"FMU"] = "JPY-HSBC-SEC"
#
#    tmp_select = (data_tmp["FMU"] == "Excluded")&(data_tmp[column_name_currency] == "JPY")
#    data_tmp.loc[tmp_select,"FMU"] = "JPY-OTHERS"
#
#    # GBP
#    chaps_bank = search_agent_bank(agent_bank_names,'Direct Participation - Bank Of England')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == chaps_bank)&(data_tmp[column_name_account_type] == "DPP")&(data_tmp[column_name_currency] == "GBP")
#    data_tmp.loc[tmp_select,"FMU"] = "GBP-CHAPS-DPP"
#
#    crest_bank = search_agent_bank(agent_bank_names,'Direct Participation - Bank Of England')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == crest_bank)&(data_tmp[column_name_account_type] == "DPS")&(data_tmp[column_name_currency] == "GBP")
#    data_tmp.loc[tmp_select,"FMU"] = "GBP-CREST-DPS"
#
#    euroclear = search_agent_bank(agent_bank_names,'EUROCLEAR BANK S.A / N.V,BRUSSELS')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == euroclear)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "GBP")
#    data_tmp.loc[tmp_select,"FMU"] = "GBP-EUROCLEAR-SEC"
#
#    rbs_bank = search_agent_bank(agent_bank_names,'ROYAL BANK OF SCOTLAND')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == rbs_bank)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "GBP")
#    data_tmp.loc[tmp_select,"FMU"] = "GBP-RBS-SEC"
#
#    tmp_select = (data_tmp["FMU"] == "Excluded")&(data_tmp[column_name_currency] == "GBP")
#    data_tmp.loc[tmp_select,"FMU"] = "GBP-ALL-OTHERS"
#
#    #CAD
#    ltvs_bank = search_agent_bank(agent_bank_names,'Direct Participation - Bank Of Canada')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == ltvs_bank)&(data_tmp[column_name_account_type] == "DPP")&(data_tmp[column_name_currency] == "CAD")
#    data_tmp.loc[tmp_select,"FMU"] = "CAD-LVTS-DPP"
#    
#    desjardins_bank = search_agent_bank(agent_bank_names,'CAISSE CENTRALE DESJARDINS')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == desjardins_bank)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "CAD")
#    data_tmp.loc[tmp_select,"FMU"] = "CAD-DESJARDINS-SEC"
#    
#    rbc_bank = search_agent_bank(agent_bank_names,'ROYAL BANK OF CANADA')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == rbc_bank)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "CAD")
#    data_tmp.loc[tmp_select,"FMU"] = "CAD-RBC-SEC"
#
#    rbc_bank = search_agent_bank(agent_bank_names,'ROYAL BANK OF CANADA')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == rbc_bank)&(data_tmp[column_name_account_type] == "CLS")&(data_tmp[column_name_currency] == "CAD")
#    data_tmp.loc[tmp_select,"FMU"] = "CAD-RBC-CLS"
#
#    tmp_select = (data_tmp["FMU"] == "Excluded")&(data_tmp[column_name_currency] == "CAD")
#    data_tmp.loc[tmp_select,"FMU"] = "CAD-ALL-OTHERS"
#
#    #EUR
#    target2_bank = search_agent_bank(agent_bank_names,'Direct Participation - ECB Target 2 Platform')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == target2_bank)&(data_tmp[column_name_account_type] == "DPP")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-TARGET2-DPP"
#
#    target2_bank = search_agent_bank(agent_bank_names,'Bank Of England')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == target2_bank)&(data_tmp[column_name_account_type] == "PRI")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-TARGET2-PRI"
#
#    Deut_bank = search_agent_bank(agent_bank_names,'DEUTSCHE BANK AG,FRANKFURT AM MAIN')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == Deut_bank)&(data_tmp[column_name_account_type] == "PRI")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-Deutsche-PRI"
#
#    Deut_bank = search_agent_bank(agent_bank_names,'INTESA SANPAOLO SPA,MILANO')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == Deut_bank)&(data_tmp[column_name_account_type] == "PRI")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-Intesa-PRI"
#    
#    euroclear_bank = search_agent_bank(agent_bank_names,'EUROCLEAR BANK S.A / N.V,BRUSSELS')
#    tmp_select = (data_tmp[column_name_agent_bank_name] == euroclear_bank)&(data_tmp[column_name_account_type] == "SEC")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-EUROCLEAR-SEC"
#
#    tmp_select = (data_tmp[column_name_account_type] == "CLS")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-ALL-CLS"
#
#    tmp_select = (data_tmp[column_name_account_type] == "DPS")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "EUR-ALL-DPS"
#
#    tmp_select = (data_tmp["FMU"] == "Excluded")&(data_tmp[column_name_currency] == "EUR")
#    data_tmp.loc[tmp_select,"FMU"] = "CAD-ALL-OTHERS"

    data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount] = data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount]*-1

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
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_ACAP_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_STS_TRANSACTION_REALTIME_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    
    if any(data_tmp["FMU"]==""):
        print("Error: FMU has missing values! Check.")
    
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

