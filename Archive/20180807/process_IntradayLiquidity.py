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
column_name_net_transaction = "NET_TOTAL_AT_TRANSCATION_TIME"
column_name_running_total = "RUNNING_TOTAL"
column_name_legal_entity = "CLEARING_MATERIAL_ENTITY"
column_name_fmu = "FMU"
column_name_datamart = "SOURCEDATAMART"
column_name_fmu_original = "FED_CHIPS_BT"
column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"

def update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby,table_name = "BCBS_248_Data_Extract_A1_Report", func=np.nansum):
#        attribute_groupby = [column_name_company,column_name_group]
    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
        start_date = datetime.datetime.strptime('2017-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2018-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        day_count = (datetime.datetime.today() - start_date).days
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
    
        day_count = 80
        start_date = datetime.datetime.today()-datetime.timedelta(day_count)
        
        for day in range(day_count):
#            day = 0
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
            else:
                print("Already in "+ date.strftime("%Y%m%d")) 
                
    if len(attribute_groupby) == 1:
        Balance_History_client[~pd.isnull(Balance_History_client.index)].to_excel(file_total_deposit_client)
    else:
        Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)

def update_table1():
    ###One dimentional Pivot Tables
    #type
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    #legal entity
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    #FMU
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    #Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    #Time
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hourminue]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    ##count
    #balance_type = column_name_transaction_amount
    #attribute_groupby = [column_name_hour]
    #file_total_deposit_client = misc_dir+"/RawData/Count_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    #update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby, func=np.count_nonzero)
    
    ##two dimensions
    # type * le
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    # type * fmu
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    # type * Data Mart
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    # type * Time
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)
    ## datamart * fmu_original
    #balance_type = column_name_transaction_amount
    #attribute_groupby = [column_name_datamart,column_name_fmu_original]
    #file_total_deposit_client = misc_dir+"/RawData/"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    #update_intraday_stat_from_A1_Extract_Table(file_total_deposit_client,balance_type,attribute_groupby)

def update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby,table_name = "BCBS_248_Data_Extract_A1_Report", func=np.nansum):
#        attribute_groupby = [column_name_company,column_name_group]
    aggregations = {
        column_name_transaction_amount: {
                'minimum' : np.nanmin,
                'maximum' : np.nanmax,
                'percentile_99' : lambda x:np.nanpercentile(x,99),
                'percentile_95' : lambda x:np.nanpercentile(x,95),
                'average' : np.nanmean,
                'medium' : np.nanmedian,
                'percentile_5' : lambda x:np.nanpercentile(x,5),
                'percentile_1' : lambda x:np.nanpercentile(x,1),
                'std' : np.nanstd,
                'count' : np.count_nonzero,
                }
        }
    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
        start_date = datetime.datetime.strptime('2017-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2018-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        day_count = (datetime.datetime.today() - start_date).days
#        day_count = 40
        for day in range(day_count):
#            day = 28
            date = start_date+datetime.timedelta(day)
            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))

            if len(table_tmp) > 0:
                table_tmp = process_bcbs_extract_a1_report(table_tmp)

                stat_result = table_tmp.groupby(attribute_groupby).agg(aggregations)
                stat_result = stat_result[column_name_transaction_amount]
                for i in range(len(attribute_groupby)):
                    stat_result = stat_result.unstack(attribute_groupby[i])

                stat_result.index.names = ['Statistics']+attribute_groupby
                
                balance = stat_result.to_frame(date.strftime("%Y%m%d"))
                if len(Balance_History_client) == 0:
                    Balance_History_client = balance
                else:
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                table_tmp = []
                gc.collect()
    else:
        Balance_History_client = pd.ExcelFile(file_total_deposit_client).parse("Sheet1")
        if attribute_groupby.__class__ is list:
            Balance_History_client = Balance_History_client.set_index(['Statistics']+attribute_groupby)
        else:
            Balance_History_client = Balance_History_client.set_index(['Statistics']+[attribute_groupby])
    
        day_count = 80
        start_date = datetime.datetime.today()-datetime.timedelta(day_count)
        
        for day in range(day_count):
#            day = 26
            date = start_date+datetime.timedelta(day)
            
            if not any(Balance_History_client.columns==date.strftime("%Y%m%d")):
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
                if len(table_tmp) > 0:
                    table_tmp = process_bcbs_extract_a1_report(table_tmp)

                    stat_result = table_tmp.groupby(attribute_groupby).agg(aggregations)
                    stat_result = stat_result[column_name_transaction_amount].unstack()
                    stat_result.index.names = ['Statistics']+attribute_groupby
                    
                    balance = stat_result.to_frame(date.strftime("%Y%m%d"))
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                    
                    table_tmp = []
                    gc.collect()
            else:
                print("Already in "+ date.strftime("%Y%m%d")) 
                
    Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)

def update_table2():
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_fmu]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_legal_entity]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_hour]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type,column_name_datamart]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)


# LNNCP
def update_intraday_stat_from_A1_Extract_Table3(file_total_deposit_client,attribute_groupby,table_name = "BCBS_248_Data_Extract_A1_Report", func=np.nansum):
#        attribute_groupby = [column_name_company,column_name_group]
    if not os.path.exists(file_total_deposit_client):
        Balance_History_client = pd.DataFrame()
        start_date = datetime.datetime.strptime('2017-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')
#        start_date = datetime.datetime.strptime('2018-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        day_count = (datetime.datetime.today() - start_date).days
#        day_count = 40
        for day in range(day_count):
#            day = 28
            date = start_date+datetime.timedelta(day)
            table_tmp = read_db(table_name,date.strftime("%Y%m%d"))

            if len(table_tmp) > 0:
                table_tmp = process_bcbs_extract_a1_report(table_tmp)

                stat_result = table_tmp.groupby(attribute_groupby).agg(aggregations)
                stat_result = stat_result[column_name_transaction_amount]
                for i in range(len(attribute_groupby)):
                    stat_result = stat_result.unstack(attribute_groupby[i])

                stat_result.index.names = ['Statistics']+attribute_groupby
                
                balance = stat_result.to_frame(date.strftime("%Y%m%d"))
                if len(Balance_History_client) == 0:
                    Balance_History_client = balance
                else:
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                table_tmp = []
                gc.collect()
    else:
        Balance_History_client = pd.ExcelFile(file_total_deposit_client).parse("Sheet1")
        if attribute_groupby.__class__ is list:
            Balance_History_client = Balance_History_client.set_index(['Statistics']+attribute_groupby)
        else:
            Balance_History_client = Balance_History_client.set_index(['Statistics']+[attribute_groupby])
    
        day_count = 80
        start_date = datetime.datetime.today()-datetime.timedelta(day_count)
        
        for day in range(day_count):
#            day = 26
            date = start_date+datetime.timedelta(day)
            
            if not any(Balance_History_client.columns==date.strftime("%Y%m%d")):
                table_tmp = read_db(table_name,date.strftime("%Y%m%d"))
                if len(table_tmp) > 0:
                    table_tmp = process_bcbs_extract_a1_report(table_tmp)

                    stat_result = table_tmp.groupby(attribute_groupby).agg(aggregations)
                    stat_result = stat_result[column_name_transaction_amount].unstack()
                    stat_result.index.names = ['Statistics']+attribute_groupby
                    
                    balance = stat_result.to_frame(date.strftime("%Y%m%d"))
                    Balance_History_client = Balance_History_client.join(balance,how="outer")
                    
                    table_tmp = []
                    gc.collect()
            else:
                print("Already in "+ date.strftime("%Y%m%d")) 
                
    Balance_History_client.to_excel(file_total_deposit_client,merge_cells=False)

def update_table3():
    balance_type = column_name_transaction_amount
    attribute_groupby = [column_name_transaction_type]
    file_total_deposit_client = misc_dir+"/RawData/Stat_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)+".xlsx"
    update_intraday_stat_from_A1_Extract_Table2(file_total_deposit_client,attribute_groupby)
    