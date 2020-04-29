# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 16:26:24 2018

@author: e620927
"""

PRODUCTION_ENVRIONMENT = True

misc_dir = "Z:/FTDRDataBase/INTRADAY_TABLES"
if PRODUCTION_ENVRIONMENT:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes-Production"
else:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"

################# Global Libraries #################
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
import datetime
import imp
import gc

################# Local Parameters  #################
import sys
sys.path.insert(0, "Z:/Charles/PyLibrary")
import Library_ReadData
imp.reload(Library_ReadData)
from Library_ReadData import read_database#, delete_database

os.chdir(code_dir)
import UpdateDatabase_Intraday_DB_IL
imp.reload(UpdateDatabase_Intraday_DB_IL)
from UpdateDatabase_Intraday_DB_IL import read_db
###update Domestic tables
#from UpdateDatabase_Intraday_DB import UPDATE_BCBS_248_Data_Extract_A1_Report
#UPDATE_BCBS_248_Data_Extract_A1_Report()

import Functions_Analysis
imp.reload(Functions_Analysis)
from Functions_Analysis import process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST

if not os.path.exists(misc_dir):
    os.makedirs(misc_dir)
    os.makedirs(misc_dir+"/RawData")

if False:
    ###update International tables
    from UpdateDatabase_Intraday_DB import UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST
    UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST("201807")

#new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME_GMT"
column_name_transaction_amount = "DER_TRANSACTION_AMOUNT_USD"
column_name_transaction_type = "TRANSACTION_TYPE"
column_name_legal_entity = "MATERIAL_ENTITY"
column_name_datamart = "SOURCEDATAMART"
column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"
column_name_currency = "CURRENCY_CODE"
column_name_nostro = "IBS_NOSTRO_NAME"

column_name_account_type = "ACCOUNT_TYPE"
column_name_agent_bank_name = "AGENT_BANK_NAME"
column_name_fmu = "FMU"

def update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name = "DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST", func=np.nansum):
#        attribute_groupby = [column_name_company,column_name_group]
#    
    if PRODUCTION_ENVRIONMENT:
#        start_date = datetime.datetime.strptime('2016-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
        start_date = datetime.datetime.strptime('2018-08-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    else:
#        start_date = datetime.datetime.strptime('2018-08-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        start_date = datetime.datetime.strptime('2016-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
        
    day_count = (datetime.datetime.today() - start_date).days

    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
#        day_count = 10
        for day in range(day_count):
#            day = 0
            date = start_date+datetime.timedelta(day)
            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
            
            if len(table_tmp) > 0:
                table_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(table_tmp)
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
#            day = 0
            date = start_date+datetime.timedelta(day)
            
            if not any(Balance_History_client.columns==date.strftime("%Y%m%d")):
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
                if len(table_tmp) > 0:
                    table_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(table_tmp)
                    balance = table_tmp.groupby(attribute_groupby).agg({balance_type:func})
                    balance.columns = [date.strftime("%Y%m%d")]
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                    table_tmp = []
                    gc.collect()
                
    if len(attribute_groupby) == 1:
        Balance_History_client[~pd.isnull(Balance_History_client.index)].to_excel(file_total_deposit_client)
    else:
        Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)

def update_table1():
#    ###One dimentional Pivot Tables
    #type
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    #legal entity
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_nostro]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
#    #currency
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_currency]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
#    
    #Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

#    #Time
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_hourminue]
#    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
#    
#    balance_type = column_name_transaction_amount
#    attribute_groupby = [column_name_hour]
#    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
#    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
#    
    ##two dimensions
    # type * le
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    # type * currency
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_agent_bank_name]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
   
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_nostro]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_currency,column_name_nostro]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_nostro,column_name_agent_bank_name,column_name_transaction_type,column_name_currency,column_name_account_type,column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_currency,column_name_account_type,column_name_fmu,column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

    # type * Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_fmu,column_name_transaction_type,column_name_account_type,column_name_currency]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_fmu,column_name_transaction_type,column_name_currency]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

    # type * Time
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_agent_bank_name,column_name_transaction_type,column_name_account_type,column_name_currency]
    file_total_deposit_client = misc_dir+"/RawData/IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_IL_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
# LNNCP
def update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client,time_interval = column_name_transaction_time,transaction_type=None,table_name = "DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST"):
#   attribute_groupby = [column_name_legal_entity]
    if PRODUCTION_ENVRIONMENT:
        start_date = datetime.datetime.strptime('2018-08-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    else:
        start_date = datetime.datetime.strptime('2016-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2018-08-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    day_count = (datetime.datetime.today() - start_date).days
    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
#        day_count = 30
        for day in range(day_count):
#            day = 1
            date = start_date+datetime.timedelta(day)
            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
    
            if len(table_tmp) > 0:
                if transaction_type is not None:
#                    transaction_type = "CREDIT"
                    table_tmp = table_tmp[table_tmp[column_name_transaction_type]==transaction_type]

                table_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(table_tmp, need_date=True)
                
                running_total_day = pd.DataFrame()
                running_total_day['STT-Total'] = table_tmp.groupby(time_interval).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()

                fmus = table_tmp[[column_name_fmu]].drop_duplicates()[column_name_fmu]
                for fmu in fmus:
                    running_total_day[fmu] = table_tmp[table_tmp[column_name_fmu]==fmu].groupby(time_interval).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()

                running_total_day = running_total_day.fillna(method='ffill').fillna(0)
                running_total_day["Date"] = date
                if len(Balance_History_client) == 0:
                    Balance_History_client = running_total_day
                else:
                    Balance_History_client = Balance_History_client.append(running_total_day)
                table_tmp = []
                gc.collect()
        Balance_History_client.to_hdf(file_total_deposit_client,key='RUNNING_TOTAL',mode='w',format = 'table')
    else:
        Balance_History_client = read_database(file_total_deposit_client)

        exist_days = set([x.strftime("%Y%m%d") for x in Balance_History_client.index])
#       day_count = 70
        Balance_History_client_to_append = pd.DataFrame()
        for day in range(day_count):
#            day = 0
            date = start_date+datetime.timedelta(day)
            if not date.strftime("%Y%m%d") in exist_days:
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
                if len(table_tmp) > 0:
                    if transaction_type is not None:
                        table_tmp = table_tmp[table_tmp[column_name_transaction_type]==transaction_type]

                    table_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(table_tmp, need_date=True)
                    
                    running_total_day = pd.DataFrame()
                    running_total_day['STT-Total'] = table_tmp.groupby(time_interval).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()

                    fmus = table_tmp[[column_name_fmu]].drop_duplicates()[column_name_fmu]
                    for fmu in fmus:
                        running_total_day[fmu] = table_tmp[table_tmp[column_name_fmu]==fmu].groupby(time_interval).agg({column_name_transaction_amount:sum})[column_name_transaction_amount].cumsum()

                    running_total_day = running_total_day.fillna(method='ffill').fillna(0)
                    running_total_day["Date"] = date

                    Balance_History_client_to_append = Balance_History_client_to_append.append(running_total_day)

                    table_tmp = []
                    gc.collect()
        
        
        if len(Balance_History_client_to_append.columns) < len(Balance_History_client.columns):
            missing_columns = list(set(Balance_History_client.columns).difference(set(Balance_History_client_to_append.columns)))
            for column in missing_columns:
                Balance_History_client_to_append[column] = np.nan
        Balance_History_client_to_append.to_hdf(file_total_deposit_client,key='RUNNING_TOTAL',append=True, format = 'table')
        
def update_table3():
    balance_type = column_name_transaction_amount
    file_total_deposit_client = misc_dir+"/HdfData/IL_RUNNINGTOTAL_"+balance_type+".hdf"
    update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client)

    file_total_deposit_client = misc_dir+"/HdfData/IL_RUNNINGTOTAL_"+balance_type+"_CREDIT.hdf"
    update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client,transaction_type="CREDIT")

    file_total_deposit_client = misc_dir+"/HdfData/IL_RUNNINGTOTAL_"+balance_type+"_DEBIT.hdf"
    update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client,transaction_type="DEBIT")

#    file_total_deposit_client = misc_dir+"/HdfData/IL_RUNNINGTOTAL_"+balance_type+"_byMinute.hdf"
#    update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client,time_interval=column_name_hourminue)
#
#    file_total_deposit_client = misc_dir+"/HdfData/IL_RUNNINGTOTAL_"+balance_type+"_CREDIT_byMinute.hdf"
#    update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client,transaction_type="CREDIT",time_interval=column_name_hourminue)
#
#    file_total_deposit_client = misc_dir+"/HdfData/IL_RUNNINGTOTAL_"+balance_type+"_DEBIT_byMinute.hdf"
#    update_intraday_stat_from_IL_A1_Extract_Table3(file_total_deposit_client,transaction_type="DEBIT",time_interval=column_name_hourminue)

def extract_percentiles(table_name):
#   table_name = "IL_RUNNINGTOTAL_"+balance_type
    Running = read_db(table_name)

    for sub_category in Running.columns:
        if sub_category == "Date":
            continue
#        sub_category = "STT-Total"
        running_tmp = Running[[sub_category,'Date']]
        unique_dates = sorted(running_tmp['Date'].drop_duplicates())
        
        running_time_df = pd.DataFrame()
        for unique_date in unique_dates:
    #        unique_date = unique_dates[0]
    
            tmp = running_tmp[running_tmp['Date']== unique_date]
            tmp = tmp.drop("Date",axis=1)
            
            tmp.index = tmp.index-datetime.timedelta(days=(unique_date.date()-datetime.date(1900, 1, 15)).days)
#            tmp.index = [x.time() for x in tmp.index]
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
#        percentiles.index = [x.strftime("%H:%M:%S") for x in percentiles.index]
#        file_name = misc_dir+"/HdfData/"+table_name+"_"+sub_category+".hdf"
#        percentiles.to_hdf(file_name,key='RUNNING_TOTAL',mode='w',format = 'table')
        file_name = misc_dir+"/RawData/"+table_name+"_"+sub_category+".xlsx"
        percentiles.to_excel(file_name)
    return(percentiles)

def update_table4():
    balance_type = column_name_transaction_amount
    extract_percentiles("IL_RUNNINGTOTAL_"+balance_type)
    extract_percentiles("IL_RUNNINGTOTAL_"+balance_type+'_CREDIT')
    extract_percentiles("IL_RUNNINGTOTAL_"+balance_type+'_DEBIT')
    
