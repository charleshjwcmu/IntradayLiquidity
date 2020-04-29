# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 16:45:11 2018

@author: e620927
"""

import datetime
import os
#new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME"
column_name_transaction_amount = "TRANSACTION_AMOUNT"
column_name_transaction_type = "TRANSACTION_TYPE"
column_name_net_transaction = "NET_TOTAL_AT_TRANSCATION_TIME"
column_name_running_total = "RUNNING_TOTAL"
column_name_legal_entity = "CLEARING_MATERIAL_ENTITY"
column_name_fmu = "FMU"
column_name_DDA = "DDA_ACCOUNT_NUMBER"
column_name_fund = "FUND"

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

def process_bcbs_extract_a1_report(data_tmp):
#    data_tmp = table_tmp
    data_tmp[column_name_transaction_time] = [datetime.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p').time() for x in data_tmp[column_name_transaction_time]]
    
    # enrich FMU 
    data_tmp["FMU"]=""
    data_tmp.loc[data_tmp["FED_CHIPS_BT"]=="CHIPS","FMU"] = "CHIPS"
    data_tmp.loc[data_tmp["FED_CHIPS_BT"]=="BT","FMU"] = "BOOK TRANSFER"
    data_tmp.loc[data_tmp["FED_CHIPS_BT"]=="FEDWR","FMU"] = "Fedwire Funds"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_FEDWIRE_CHIPS_TRANSACTION_FUNDING_CHIPS_SIDE") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "CHIPS"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_CHK_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "FED CHK"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_STS_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_ACH_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "FED ACH"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_FICC_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "DTCC - FICC"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_NSS_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Funds"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_ACAP_TRANSACTION_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    data_tmp.loc[(data_tmp["SOURCEDATAMART"]=="DM_STS_TRANSACTION_REALTIME_STEP1") & (~data_tmp["FED_CHIPS_BT"].isin(['CHIPS','BT','FEDWR'])),"FMU"] = "Fedwire Securities"
    
    # enrich missing DDA with Fund number
    data_tmp[column_name_transaction_amount] = data_tmp[column_name_transaction_amount].apply(clean_number)
    data_tmp[column_name_net_transaction] = data_tmp[column_name_net_transaction].apply(clean_number)
    data_tmp[column_name_running_total] = data_tmp[column_name_running_total].apply(clean_number)

    data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount] = data_tmp.loc[data_tmp[column_name_transaction_type]=="DEBIT",column_name_transaction_amount]*-1

    data_tmp.loc[data_tmp[column_name_transaction_type] == "BOOK TRANSFER",column_name_transaction_amount] = 0

    data_tmp.index = data_tmp[column_name_transaction_time]
    data_tmp = data_tmp.sort_index()
    data_tmp['TimeBucket'] = [format_hour(x.hour) + " - " + format_hour(x.hour+1) for x in data_tmp.index]
    
    data_tmp['TimeMinute'] = [format_hour(x.hour) + ":" + format_hour(x.minute) for x in data_tmp.index]

    return(data_tmp)

