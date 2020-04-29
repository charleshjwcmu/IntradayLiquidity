# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 16:26:24 2018

@author: e620927
"""

PRODUCTION_ENVRIONMENT = True

misc_dir = "Z:/FTDRDataBase/INTRADAY_TABLES"
if PRODUCTION_ENVRIONMENT:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes-Production"
    days_need_update = 60
else:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"
    days_need_update = 60

################# Global Libraries #################
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import datetime
import imp
import gc
import time

################# Local Parameters  #################
import sys
sys.path.insert(0, "Z:/Charles/PyLibrary")
import Library_ReadData
imp.reload(Library_ReadData)
from Library_ReadData import read_database#, delete_database

os.chdir(code_dir)
import UpdateDatabase_Intraday_DB
imp.reload(UpdateDatabase_Intraday_DB)
from UpdateDatabase_Intraday_DB import read_db
###update Domestic tables
#from UpdateDatabase_Intraday_DB import UPDATE_BCBS_248_Data_Extract_A1_Report
#UPDATE_BCBS_248_Data_Extract_A1_Report()

import Functions_Analysis
imp.reload(Functions_Analysis)
from Functions_Analysis import process_bcbs_extract_a1_report

if not os.path.exists(misc_dir):
    os.makedirs(misc_dir)
    os.makedirs(misc_dir+"/RawData")

if False:
    ###update International tables
    from UpdateDatabase_Intraday_DB import UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST
    UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST()

#new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME"
column_name_transaction_amount = "TRANSACTION_AMOUNT"
column_name_transaction_type = "TRANSACTION_TYPE"
#column_name_net_transaction = "NET_TOTAL_AT_TRANSCATION_TIME"
#column_name_running_total = "RUNNING_TOTAL"
column_name_legal_entity = "CLEARING_MATERIAL_ENTITY"
column_name_datamart = "SOURCEDATAMART"
column_name_fmu_original = "FED_CHIPS_BT"
column_name_fmu = "FMU"
column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"
column_name_interval = "TimeInterval"
column_name_15minutes = "Time15Minute"
column_name_30minutes = "Time30Minute"
column_name_60minutes = "Time60Minute"

def update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name = "BCBS_248_Data_Extract_A1_Report", func=np.nansum):
#        attribute_groupby = [column_name_company,column_name_group]
    if table_name == "BCBS_248_Data_Extract_A1_Report":
#        start_date = datetime.datetime.strptime('2018-06-25 00:00:00', '%Y-%m-%d %H:%M:%S')
        start_date = datetime.datetime.strptime('2016-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')

    elif table_name == "DM_RTIM_DOM_ALL_TRANSACTION_STEP3":
        start_date = datetime.datetime.today() - datetime.timedelta(days = days_need_update)
#        start_date = datetime.datetime.strptime('2018-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    day_count = (datetime.datetime.today() - start_date).days

    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
#        day_count = 10
        for day in range(day_count):
#            day = 0
            date = start_date+datetime.timedelta(day)
            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))

            if len(table_tmp) > 0:
                table_tmp = process_bcbs_extract_a1_report(table_tmp)
                balance = table_tmp.groupby(attribute_groupby).agg({balance_type:func})
                balance.columns = [date.strftime("%Y%m%d")]
                    
                if len(Balance_History_client) == 0:
                    Balance_History_client = balance
                else:
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                table_tmp = []
                gc.collect()
    else:
        Balance_History_client = pd.ExcelFile(file_total_deposit_client).parse("Sheet1")
        if attribute_groupby.__class__ is list:
            Balance_History_client = Balance_History_client.set_index(attribute_groupby)
        else:
            Balance_History_client = Balance_History_client.set_index([attribute_groupby])
            
#        day_count = 80
#        start_date = datetime.datetime.today()-datetime.timedelta(day_count)
            
        for day in range(day_count):
#            day = 15
            date = start_date+datetime.timedelta(day)
            
            if not any(Balance_History_client.columns==date.strftime("%Y%m%d")):
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
                if len(table_tmp) > 0:
                    table_tmp = process_bcbs_extract_a1_report(table_tmp)
                    balance = table_tmp.groupby(attribute_groupby).agg({balance_type:func})
                    balance.columns = [date.strftime("%Y%m%d")]
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                    table_tmp = []
                    gc.collect()
#            else:
#                print("Already in "+ date.strftime("%Y%m%d")) 
                
    if len(attribute_groupby) == 1:
        Balance_History_client[~pd.isnull(Balance_History_client.index)].to_excel(file_total_deposit_client)
    else:
        Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)

def update_table1(table_name = "BCBS_248_Data_Extract_A1_Report"):
    start_time = time.time()
    ###One dimentional Pivot Tables
    #type
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    
    #legal entity
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    
    #FMU
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    
    #Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    
    ### Time
    # by minute
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hourminue]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    
    # by hour
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    
    # by 15 minutes
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_15minutes]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)

    # by 30 minutes
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_30minutes]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
 
    # by 60 minutes
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_60minutes]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)

    ##two dimensions
    # type * le
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    # type * fmu
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    # type * Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)
    # type * Time
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name)

    print("Execution runtime to update table 1 (pivot tables) is "+str(round(time.time()-start_time,0))+" seconds")

def update_intraday_stat_from_A1_Extract_Table_Fed_Balance(file_total_deposit_client):
#        attribute_groupby = [column_name_company,column_name_group]
    if PRODUCTION_ENVRIONMENT:
        start_date = datetime.datetime.today() - datetime.timedelta(days = days_need_update)
    else:
        start_date = datetime.datetime.strptime('2016-01-02 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2017-01-02 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2018-06-20 00:00:00', '%Y-%m-%d %H:%M:%S')
    day_count = (datetime.datetime.today() - start_date).days

    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
        Balance_History_client_error = pd.DataFrame()
#        day_count = 10
        for day in range(day_count):
#            day = 1
            date = start_date+datetime.timedelta(day)
            if date < datetime.datetime.strptime("20180701","%Y%m%d"):
                table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY"
            else:
                table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3"
            
            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))

            if len(table_tmp) > 0:
                fed_balance = table_tmp.loc[table_tmp[column_name_datamart]=='MTS_ABAL_TRANSACTION',column_name_transaction_amount]
                if len(fed_balance) == 1:
                    Balance_History_client[date.strftime("%Y%m%d")] = fed_balance.get_values()
                else:
                    Balance_History_client_error = Balance_History_client_error.append(pd.DataFrame({"Date":[date.strftime("%Y%m%d")],"Value":[len(fed_balance)]}))
                table_tmp = []
                gc.collect()
            Balance_History_client.index = ["Fed_Balance"]
    else:
        Balance_History_client = pd.ExcelFile(file_total_deposit_client).parse("Sheet1")
        Balance_History_client_error = pd.DataFrame()
            
        for day in range(day_count):
#            day = 0
            date = start_date+datetime.timedelta(day)
            
            if not any(Balance_History_client.columns==date.strftime("%Y%m%d")):
                if date < datetime.datetime.strptime("20180701","%Y%m%d"):
                    table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY"
                else:
                    table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3"
                
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
    
                if len(table_tmp) > 0:
                    fed_balance = table_tmp.loc[table_tmp[column_name_datamart]=='MTS_ABAL_TRANSACTION',column_name_transaction_amount]
                    if len(fed_balance) == 1:
                        Balance_History_client[date.strftime("%Y%m%d")] = fed_balance.get_values()
                    else:
                        Balance_History_client_error = Balance_History_client_error.append(pd.DataFrame({"Date":[date.strftime("%Y%m%d")],"Value":[len(fed_balance)]}))
                    table_tmp = []
                    gc.collect()
#            else:
#                print("Already in "+ date.strftime("%Y%m%d")) 
                
    Balance_History_client = Balance_History_client[~pd.isnull(Balance_History_client.index)]
    Balance_History_client.transpose().sort_index().transpose().to_excel(file_total_deposit_client)
    return(Balance_History_client_error)

def update_table_fed_balance():
    start_time = time.time()
    file_total_deposit_client = misc_dir+"/RawData/Fed_Balance.xlsx"
    update_intraday_stat_from_A1_Extract_Table_Fed_Balance(file_total_deposit_client)
    print("Execution runtime to update Fed balance table is "+str(round(time.time()-start_time,0))+" seconds")

def update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type=None,table_name = "BCBS_248_Data_Extract_A1_Report",FedBalance=False,aggregate_by=column_name_transaction_time):
#   attribute_groupby = [column_name_legal_entity]
    if table_name == "BCBS_248_Data_Extract_A1_Report":
        start_date = datetime.datetime.strptime('2017-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2016-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
    elif table_name == "DM_RTIM_DOM_ALL_TRANSACTION_STEP3":
        start_date = datetime.datetime.today() - datetime.timedelta(days = days_need_update)

    legal_entity = ['SSBT BOSTON','SSBT NEW YORK']
    fmus = ['CHIPS','Fedwire Funds','Fedwire Securities', 'DTCC - FICC']

    if FedBalance:
        Fed_balance = read_db("Fed_Balance").transpose()
        Fed_balance.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in Fed_balance.index]
#        fed_balance = Fed_balance.loc[date,'Fed_Balance'] 

    day_count = (datetime.datetime.today() - start_date).days
    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
#        day_count = 30
        for day in range(day_count):
#            day = 0
            date = start_date+datetime.timedelta(day)
            if FedBalance and date not in Fed_balance.index:
                print("Warning: Cannot find start of day fed balance: skip " + date.strftime("%Y%m%d"))
                continue
            elif FedBalance and date in Fed_balance.index:
                fed_balance = Fed_balance.loc[date,'Fed_Balance'] 
            else:
                fed_balance = 0

            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
    
            if len(table_tmp) > 0:
                if transaction_type is not None:
#                    transaction_type = "CREDIT"
                    table_tmp = table_tmp[table_tmp[column_name_transaction_type]==transaction_type]

                table_tmp = process_bcbs_extract_a1_report(table_tmp, need_date=True)
                
                running_total_day = pd.DataFrame()
                running_total_day['STT-Total'] = table_tmp.groupby(aggregate_by).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum() + fed_balance
                if not FedBalance:
                    for le in legal_entity:
                        running_total_day[le] = table_tmp[table_tmp[column_name_legal_entity]==le].groupby(aggregate_by).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()
    
                    for fmu in fmus:
                        running_total_day[fmu] = table_tmp[table_tmp["FMU"]==fmu].groupby(aggregate_by).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()
                
                running_total_day = running_total_day.fillna(method='ffill').fillna(0)
                
                if len(Balance_History_client) == 0:
                    Balance_History_client = running_total_day
                else:
                    Balance_History_client = Balance_History_client.append(running_total_day)
                table_tmp = []
                gc.collect()
#                Balance_History_client.plot()
        Balance_History_client.to_hdf(file_total_deposit_client,key='RUNNING_TOTAL',mode='w',format = 'table')
    else:
        Balance_History_client = read_database(file_total_deposit_client)

        exist_days = set([x.strftime("%Y%m%d") for x in Balance_History_client.index])
#       day_count = 70
        Balance_History_client_to_append = pd.DataFrame()
        for day in range(day_count):
#            day = 28
            date = start_date+datetime.timedelta(day)
            if FedBalance and date not in Fed_balance.index:
                continue
            elif FedBalance and date in Fed_balance.index:
                fed_balance = Fed_balance.loc[date,'Fed_Balance'] 
            else:
                fed_balance = 0

            if not date.strftime("%Y%m%d") in exist_days:
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
                if len(table_tmp) > 1e3:
                    if transaction_type is not None:
                        table_tmp = table_tmp[table_tmp[column_name_transaction_type]==transaction_type]

                    table_tmp = process_bcbs_extract_a1_report(table_tmp, need_date=True)
                    
                    running_total_day = pd.DataFrame()
                    running_total_day['STT-Total'] = table_tmp.groupby(aggregate_by).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum() + fed_balance
    
                    if not FedBalance: 
                        for le in legal_entity:
                            running_total_day[le] = table_tmp[table_tmp[column_name_legal_entity]==le].groupby(aggregate_by).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()
    #                    fmus = ['CHIPS','Fedwire Funds','Fedwire Securities', 'DTCC - FICC']
                        for fmu in fmus:
                            running_total_day[fmu] = table_tmp[table_tmp["FMU"]==fmu].groupby(aggregate_by).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()
                    
                    running_total_day = running_total_day.fillna(method='ffill').fillna(0)

                    Balance_History_client_to_append = Balance_History_client_to_append.append(running_total_day)

                    table_tmp = []
                    gc.collect()
#            else:
#                print("Already in "+ date.strftime("%Y%m%d")) 
        Balance_History_client_to_append.head()
        Balance_History_client.head()
        
        if len(Balance_History_client_to_append) > 0:
            Balance_History_client_to_append.to_hdf(file_total_deposit_client,key='RUNNING_TOTAL',append=True, format = 'table')
        
#        read_database(file_total_deposit_client).shape
#        read_database(file_total_deposit_client).plot()
        
def update_table3(table_name = "BCBS_248_Data_Extract_A1_Report"):
    start_time = time.time()

    balance_type = column_name_transaction_amount
    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+".hdf"
    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,table_name=table_name)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_CREDIT.hdf"
    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type="CREDIT",table_name=table_name)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_DEBIT.hdf"
    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type="DEBIT",table_name=table_name)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_with_FedBalance.hdf"
    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,table_name=table_name,FedBalance=True)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_CREDIT_with_FedBalance.hdf"
    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type="CREDIT",table_name=table_name,FedBalance=True)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_DEBIT_with_FedBalance.hdf"
    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type="DEBIT",table_name=table_name,FedBalance=True)
    print("Execution runtime to update table 3 (Running balance) is "+str(round(time.time()-start_time,0))+" seconds")

#    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_CREDIT_15min.hdf"
#    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type="CREDIT",table_name=table_name,aggregate_by=column_name_interval)
#
#    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_DEBIT_15min.hdf"
#    update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,transaction_type="DEBIT",table_name=table_name,aggregate_by=column_name_interval)
    
#    
#def ad_hoc():
#    debit = read_db("RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_15min").to_excel(misc_dir+"/RawData/RUNNINGTOTAL_"+balance_type+"_DEBIT_15min.xlsx")
#    credit = read_db("RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_15min").to_excel(misc_dir+"/RawData/RUNNINGTOTAL_"+balance_type+"_CREDIT_15min.xlsx")


def extract_percentiles(table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT"):
#    Running = read_db("RUNNINGTOTAL_TRANSACTION_AMOUNT_with_FedBalance")
    Running = read_db(table_name)

    for sub_category in Running.columns:
#        sub_category = "STT-Total"
        running_tmp = Running[[sub_category]]
        unique_dates = set([x.strftime("%Y-%m-%d") for x in running_tmp.index])
        unique_dates = sorted([datetime.datetime.strptime(x,"%Y-%m-%d") for x in unique_dates])
    
        running_time_df = pd.DataFrame()
        for unique_date in unique_dates:
    #        unique_date = unique_dates[0]
            
            tmp = running_tmp[(running_tmp.index>=unique_date) & (running_tmp.index<unique_date+datetime.timedelta(days=1))]
            tmp.index = [x.time() for x in tmp.index]
            tmp.columns = [unique_date]
            if len(running_time_df) == 0:
                running_time_df = tmp
            else:
                running_time_df = running_time_df.join(tmp,how='outer')
        running_time_df = running_time_df.fillna(method='ffill').fillna(0)
#    running_time_df.plot()
        percentiles = pd.DataFrame({"1th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,1),axis=1),\
                                    "5th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,5),axis=1),\
                                    "25th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,25),axis=1),\
                                    "50th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,50),axis=1),\
                                    "75th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,75),axis=1),\
                                    "95th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,95),axis=1),\
                                    "99th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,99),axis=1)})
        percentiles = percentiles[["1th Percentile","5th Percentile","25th Percentile","50th Percentile","75th Percentile","95th Percentile","99th Percentile"]]

#        percentiles = pd.DataFrame({"5th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,5),axis=1),\
#                        "25th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,25),axis=1),\
#                        "50th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,50),axis=1),\
#                        "75th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,75),axis=1),\
#                        "95th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,95),axis=1)})
#        percentiles = percentiles[["5th Percentile","25th Percentile","50th Percentile","75th Percentile","95th Percentile"]]
#        percentiles.plot()
        percentiles.index = [x.strftime("%H:%M:%S") for x in percentiles.index]
#        file_name = misc_dir+"/HdfData/"+table_name+"_"+sub_category+".hdf"
#        percentiles.to_hdf(file_name,key='RUNNING_TOTAL',mode='w',format = 'table')
        file_name = misc_dir+"/RawData/"+table_name+"_"+sub_category+".xlsx"
        percentiles.to_excel(file_name)
    return(percentiles)

def update_table4():
    start_time = time.time()
    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT')
    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_with_FedBalance')

    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT')
    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_with_FedBalance')

    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT')
    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_with_FedBalance')
    print("Execution runtime to update table 4 (percentiles) is "+str(round(time.time()-start_time,0))+" seconds")

#    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_15min')
#    extract_percentiles('RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_15min')

#    tmp = read_db("RUNNINGTOTAL_TRANSACTION_AMOUNT")
    
#
#def extract_percentiles_by_timeinterval(table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT"):
##    Running = read_db("RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT")
#    Running = read_db(table_name)
#
#    for sub_category in Running.columns:
##        sub_category = "STT-Total"
#        running_tmp = Running[[sub_category]]
#        unique_dates = set([x.strftime("%Y-%m-%d") for x in running_tmp.index])
#        unique_dates = sorted([datetime.datetime.strptime(x,"%Y-%m-%d") for x in unique_dates])
#    
#        running_time_df = pd.DataFrame()
#        for unique_date in unique_dates:
#    #        unique_date = unique_dates[0]
#            
#            tmp = running_tmp[(running_tmp.index>=unique_date) & (running_tmp.index<unique_date+datetime.timedelta(days=1))]
#            tmp.index = [x.time() for x in tmp.index]
#            tmp.columns = [unique_date]
#            
#            tmp.resample('15T').sum()
#            tmp.resample('15T').last()
#
#            if len(running_time_df) == 0:
#                running_time_df = tmp
#            else:
#                running_time_df = running_time_df.join(tmp,how='outer')
#        running_time_df = running_time_df.fillna(method='ffill').fillna(0)
##    running_time_df.plot()
#        percentiles = pd.DataFrame({"1th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,1),axis=1),\
#                                    "5th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,5),axis=1),\
#                                    "25th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,25),axis=1),\
#                                    "50th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,50),axis=1),\
#                                    "75th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,75),axis=1),\
#                                    "95th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,95),axis=1),\
#                                    "99th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,99),axis=1)})
#        percentiles = percentiles[["1th Percentile","5th Percentile","25th Percentile","50th Percentile","75th Percentile","95th Percentile","99th Percentile"]]
#
##        percentiles = pd.DataFrame({"5th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,5),axis=1),\
##                        "25th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,25),axis=1),\
##                        "50th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,50),axis=1),\
##                        "75th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,75),axis=1),\
##                        "95th Percentile":running_time_df.apply(lambda x: np.nanpercentile(x,95),axis=1)})
##        percentiles = percentiles[["5th Percentile","25th Percentile","50th Percentile","75th Percentile","95th Percentile"]]
##        percentiles.plot()
#        percentiles.index = [x.strftime("%H:%M:%S") for x in percentiles.index]
##        file_name = misc_dir+"/HdfData/"+table_name+"_"+sub_category+".hdf"
##        percentiles.to_hdf(file_name,key='RUNNING_TOTAL',mode='w',format = 'table')
#        file_name = misc_dir+"/RawData/"+table_name+"_"+sub_category+".xlsx"
#        percentiles.to_excel(file_name)
#    return(percentiles)
#
#
#def update_table4_by_time_interval():
#    extract_percentiles_by_timeinterval('RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT')
#    extract_percentiles_by_timeinterval('RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT')

def Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end):
    if os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.ExcelFile(file_total_deposit_client).parse("Sheet1")
    else:
        print("Table does not exist: " + file_total_deposit_client)
        return()
    if attribute_groupby.__class__ is list:
        Balance_History_client = Balance_History_client.set_index(attribute_groupby)
    else:
        Balance_History_client = Balance_History_client.set_index([attribute_groupby])
    
    Balance_History_client = Balance_History_client.transpose()
    Balance_History_client.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in Balance_History_client.index]
    
    Balance_History_client = Balance_History_client[~(Balance_History_client.index >= cleanup_start) & (Balance_History_client.index <= cleanup_end)]
    
    Balance_History_client.index = [x.strftime("%Y%m%d") for x in Balance_History_client.index]
    
    Balance_History_client = Balance_History_client.dropna(axis=1,how='all').transpose()

    if len(attribute_groupby) == 1:
        Balance_History_client[~pd.isnull(Balance_History_client.index)].to_excel(file_total_deposit_client)
    else:
        Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)

def Cleanup_running_total_history(file_total_deposit_client,cleanup_start,cleanup_end):
    if os.path.exists(file_total_deposit_client):
        Balance_History_client = read_database(file_total_deposit_client)    
    else:
        print("Table does not exist: " + file_total_deposit_client)
        return()
        
    Balance_History_client = Balance_History_client[~(Balance_History_client.index >= cleanup_start) & (Balance_History_client.index <= cleanup_end)]

    if len(Balance_History_client) > 0:
        Balance_History_client.to_hdf(file_total_deposit_client,key='RUNNING_TOTAL',mode='w',format = 'table')

def Cleanup_tables(cleanup_start,cleanup_end=datetime.datetime.today()):
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    #legal entity
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    #FMU
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    #Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    #Time
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hourminue]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    ##two dimensions
    # type * le
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    # type * fmu
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    # type * Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    # type * Time
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    Cleanup_history(file_total_deposit_client,balance_type,attribute_groupby,cleanup_start,cleanup_end)
    
    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+".hdf"
    Cleanup_running_total_history(file_total_deposit_client,cleanup_start,cleanup_end)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_CREDIT.hdf"
    Cleanup_running_total_history(file_total_deposit_client,cleanup_start,cleanup_end)

    file_total_deposit_client = misc_dir+"/HdfData/RUNNINGTOTAL_"+balance_type+"_DEBIT.hdf"
    Cleanup_running_total_history(file_total_deposit_client,cleanup_start,cleanup_end)


#def update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby,table_name = "BCBS_248_Data_Extract_A1_Report", func=np.nansum):
##        attribute_groupby = [column_name_company,column_name_group]
#    aggregations = {
#        column_name_transaction_amount: {
#                'minimum' : np.nanmin,
#                'maximum' : np.nanmax,
#                'percentile_99' : lambda x:np.nanpercentile(x,99),
#                'percentile_95' : lambda x:np.nanpercentile(x,95),
#                'average' : np.nanmean,
#                'medium' : np.nanmedian,
#                'percentile_5' : lambda x:np.nanpercentile(x,5),
#                'percentile_1' : lambda x:np.nanpercentile(x,1),
#                'std' : np.nanstd,
#                'count' : np.count_nonzero,
#                }
#        }
#    start_date = datetime.datetime.strptime('2017-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
##        start_date = datetime.datetime.strptime('2018-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
#    day_count = (datetime.datetime.today() - start_date).days
#
#    if not os.path.exists(file_total_deposit_client):
#        Balance_History_client = pd.DataFrame()
##        day_count = 40
#        for day in range(day_count):
##            day = 28
#            date = start_date+datetime.timedelta(day)
#            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
#
#            if len(table_tmp) > 0:
#                table_tmp = process_bcbs_extract_a1_report(table_tmp)
#
#                stat_result = table_tmp.groupby(attribute_groupby).agg(aggregations)
#                stat_result = stat_result[column_name_transaction_amount]
#                for i in range(len(attribute_groupby)):
#                    stat_result = stat_result.unstack(attribute_groupby[i])
#
#                stat_result.index.names = ['Statistics']+attribute_groupby
#                
#                balance = stat_result.to_frame(date.strftime("%Y%m%d"))
#                if len(Balance_History_client) == 0:
#                    Balance_History_client = balance
#                else:
#                    Balance_History_client = Balance_History_client.join(balance,how="outer")
#                table_tmp = []
#                gc.collect()
#    else:
#        Balance_History_client = pd.ExcelFile(file_total_deposit_client).parse("Sheet1")
#        if attribute_groupby.__class__ is list:
#            Balance_History_client = Balance_History_client.set_index(['Statistics']+attribute_groupby)
#        else:
#            Balance_History_client = Balance_History_client.set_index(['Statistics']+[attribute_groupby])
#    
##        day_count = 80
##        start_date = datetime.datetime.today()-datetime.timedelta(day_count)
#        
#        for day in range(day_count):
##            day = 26
#            date = start_date+datetime.timedelta(day)
#            
#            if not any(Balance_History_client.columns==date.strftime("%Y%m%d")):
#                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
#                if len(table_tmp) > 0:
#                    table_tmp = process_bcbs_extract_a1_report(table_tmp)
#
#                    stat_result = table_tmp.groupby(attribute_groupby).agg(aggregations)
#                    stat_result = stat_result[column_name_transaction_amount].unstack()
#                    stat_result.index.names = ['Statistics']+attribute_groupby
#                    
#                    balance = stat_result.to_frame(date.strftime("%Y%m%d"))
#                    Balance_History_client = Balance_History_client.join(balance,how="outer")
#                    
#                    table_tmp = []
#                    gc.collect()
##            else:
##                print("Already in "+ date.strftime("%Y%m%d")) 
#                
#    Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)
#
#def update_table2():
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_transaction_type]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_fmu]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_hour]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_datamart]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_transaction_type,column_name_fmu]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_transaction_type,column_name_legal_entity]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_transaction_type,column_name_hour]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_transaction_type,column_name_datamart]
#    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
