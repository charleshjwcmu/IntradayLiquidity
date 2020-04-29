# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 09:52:51 2018

@author: e620927
"""

PATH_DB = "Z:/FTDRDataBase/"
misc_dir = "Z:/FTDRDataBase/INTRADAY_TABLES"

#PATH_DB = "//mfmaog02/ERMShared/Treasury Risk/Liquidity Risk/LCR - 5G Mapping/5G Data"
PRODUCTION_ENVRIONMENT = True
################# Global Parameters  #################
if PRODUCTION_ENVRIONMENT:
    days_need_update = 10
else:
    days_need_update = 30
#    days_need_update = 273

import os
import pandas as pd
import datetime
import time
import imp
import glob
import sys
sys.path.insert(0, "Z:/Charles/PyLibrary")
import Library_ReadData
imp.reload(Library_ReadData)
from Library_ReadData import read_database, delete_database

UPDATE = True
#UPDATE = False

#excel format table
def update_db_excel(table_name,raw_directory,out_directory,date_list=None):
#    date_list=["20170930"]
    if date_list == None:
        base = datetime.datetime.today()
        date_list = [(base - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range(0, days_need_update)]

    if not os.path.exists(raw_directory):
        os.makedirs(raw_directory)
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
                 
    for date in date_list:
    #    date = date_list[18]
        file_name_source = raw_directory+"/"+table_name+"_"+date+".xlsx"
        file_name_output = out_directory+"/"+table_name+"_"+date+".hdf"
        
        if os.path.exists(file_name_source) and (not os.path.exists(file_name_output)):
            print("New Source File Found: "+file_name_source)
            start_time = time.time()
            data = pd.ExcelFile(file_name_source)
            
            data_excel = data.parse("Sheet1")
            
            if "Sheet2" in data.sheet_names:
                data_excel2 = data.parse("Sheet2")
                if (len(data_excel2.index) > 0):
                    data_excel = data_excel.append(data_excel2)
            
            print(table_name+"/"+"Read Excel data using " + str(round(time.time()-start_time,0)) + " seconds")
#            print(data_excel["AS_OF_DATE"].unique())
            start_time = time.time()
            data_excel.to_hdf(file_name_output,"w",table=True)
            print(table_name+"/"+"Convert HDF data using " + str(round(time.time()-start_time,0)) + " seconds")
            
        elif not os.path.exists(file_name_source):
            print(table_name+"/"+date + ": Source File Not Found")
        elif os.path.exists(file_name_output):
            print(table_name+"/"+date + ": Data Conversion has already completed")
            
def update_daily_tables():
    table_names = ["DM_RTIM_DOM_ALL_TRANSACTION_STEP3"]
    for table_name in table_names:
        raw_directory = PATH_DB+table_name+"/RawData"
        out_directory = PATH_DB+table_name+"/HdfData"
        update_db_excel(table_name,raw_directory,out_directory)

def update_db_txt_DM_IDLM_ALL_TRANSACTION_STEP2(table_name,raw_directory,out_directory,date_list=None):
#    date_list=["20171108"]
    if date_list == None:
        base = datetime.datetime.today()
        date_list = [(base - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range(0, days_need_update)]

    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    
    for date in date_list:
    #    date = date_list[0]
        file_name_source = raw_directory+"/"+table_name+"_"+date+".txt"
        
        if os.path.exists(file_name_source):
            print(table_name+"/"+"Source File Found: "+file_name_source)
            start_time = time.time()
            
            data_chunks = pd.read_table(file_name_source,chunksize =10**5)
            existing_date_list = set()
            for i, chunk in enumerate(data_chunks):
                chunk['ASOF'] = [datetime.datetime.strptime(x,"%m/%d/%Y 12:00:00 AM") for x in chunk['ASOF']]
                dates = chunk['ASOF'].drop_duplicates()
                dates = sorted(dates)
                for chunkdate in dates:
    #                chunkdate = dates[0]
                    print("Process Date " + chunkdate.strftime("%Y%m%d"))
                    file_name_output = raw_directory+"/"+table_name+"_"+chunkdate.strftime("%Y%m%d")+".xlsx"
                    file_name_output_hdf = out_directory+"/"+table_name+"_"+chunkdate.strftime("%Y%m%d")+".hdf"
                    
                    if os.path.exists(file_name_output) and (not chunkdate in existing_date_list):
                        print("Excel Already Existed - No Excel Created for date/" + chunkdate.strftime("%Y%m%d"))
                    elif os.path.exists(file_name_output) and (chunkdate in existing_date_list):
                        print("Excel Already Existed - Just append more data for date/" + chunkdate.strftime("%Y%m%d"))
                        chunk_data_existed = pd.ExcelFile(file_name_output).parse('Sheet1')
                        print("  Existing Excel Shape: " + str(chunk_data_existed.shape[0]) + " / " + str(chunk_data_existed.shape[1]))

                        chunk_data = chunk[chunk['ASOF']==chunkdate]
                        chunk_data = chunk_data_existed.append(chunk_data)
                        print("  New Excel Shape: " + str(chunk_data.shape[0]) + " / " + str(chunk_data.shape[1]))
                        
                        delete_database(file_name_output)
                        delete_database(file_name_output_hdf)
                        
                        chunk_data.to_excel(file_name_output)
                        chunk_data.to_hdf(file_name_output_hdf,"w",table=True)
                        
                    elif not os.path.exists(file_name_output) and (not chunkdate in existing_date_list):
                        print("New Excel Created for date/" + chunkdate.strftime("%Y%m%d"))
                        chunk_data = chunk[chunk['ASOF']==chunkdate]
                        print("  Excel Shape: " + str(chunk_data.shape[0]) + " / " + str(chunk_data.shape[1]))

                        delete_database(file_name_output)
                        delete_database(file_name_output_hdf)
                        
                        chunk_data.to_excel(file_name_output)
                        chunk_data.to_hdf(file_name_output_hdf,"w",table=True)
                        existing_date_list.update([chunkdate])
                    elif not os.path.exists(file_name_output) and (chunkdate in existing_date_list):
                        print("Algorithmic Error")
                        print(chunkdate)
                        print("==")
                        print(existing_date_list)
            print(table_name+"/"+"Convert data using " + str(round(time.time()-start_time,0)) + " seconds")
            
        elif not os.path.exists(file_name_source):
            print(table_name+"/"+date + ": Source File Not Found")

if False:
    table_name = "DM_IDLM_ALL_TRANSACTION_STEP2"
    raw_directory = PATH_DB+table_name+"/RawData"
    out_directory = PATH_DB+table_name+"/HdfData"
    update_db_txt_DM_IDLM_ALL_TRANSACTION_STEP2(table_name,raw_directory,out_directory,date_list=["20170810"])

def update_db_txt_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(table_name,raw_directory,out_directory,date_list=None):
#    date_list=["20171108"]
    if date_list == None:
        print("Need to input dates")
        return()

    file_directory = "Z:/GTRM_Special_Projects/Intraday Liquidity Modeling/Data/International Extracts"

    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    if not os.path.exists(raw_directory):
        os.makedirs(raw_directory)
    
    for date in date_list:
    #    date = date_list[0]
        file_name_source = file_directory+"/"+date+"_"+table_name+" 1"+".txt"
        
        if os.path.exists(file_name_source):
            print(table_name+"/"+"Source File Found: "+file_name_source)
            start_time = time.time()
            
#            data_chunks = pd.read_table(file_name_source,chunksize =10**5)
            data_raw = pd.read_table(file_name_source)
#            data_raw.shape
            unique_dates = data_raw['ASOF'].drop_duplicates()
            for day in unique_dates:
#                date = unique_dates[0]
                output_date = datetime.datetime.strptime(day,"%m/%d/%Y 12:00:00 AM")
                file_name_output = raw_directory+"/"+table_name+"_"+output_date.strftime("%Y%m%d")+".xlsx"
                file_name_output_hdf = out_directory+"/"+table_name+"_"+output_date.strftime("%Y%m%d")+".hdf"
                
                if not os.path.exists(file_name_output):
                    data_raw[data_raw['ASOF'] == day].to_excel(file_name_output)
                else:
                    print("excel exist already: " + day)
                    
                if not os.path.exists(file_name_output_hdf):
                    data_raw[data_raw['ASOF'] == day].to_hdf(file_name_output_hdf,"w",table=True)
                else:
                    print("hdf exist already: " + day)

            print(table_name+"/"+"Convert data using " + str(round(time.time()-start_time,0)) + " seconds")
            
        elif not os.path.exists(file_name_source):
            print(table_name+"/"+date + ": Source File Not Found")

def UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(date_list=None):
    table_name = "DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST"
    raw_directory = PATH_DB+table_name+"/RawData"
    out_directory = PATH_DB+table_name+"/HdfData"
    if date_list == None:
        print("No date is input to update table " + table_name)
        return()
        
    if date_list.__class__ == str:
        date_list = [date_list]
#    ["201601",
#    date_list = ["201602","201603","201604","201605","201606","201607","201608","201609","201610","201611","201612",
#     "201701","201702","201703","201704","201705","201706","201707","201708","201709","201710","201711","201712",
#     "201801","201802","201803","201804","201805"]
#    ,"201606","201607","201608","201609","201610","201611","201612",]
    update_db_txt_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(table_name,raw_directory,out_directory,date_list)


def update_db_txt_BCBS_248_Data_Extract_A1_Report(table_name,raw_directory,out_directory):
#    date_list=["20171108"]

    file_directory = "Z:/GTRM_Special_Projects/Intraday Liquidity Modeling/Data/USD Daily Extracts"

    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    if not os.path.exists(raw_directory):
        os.makedirs(raw_directory)
    
#    update_start = (datetime.datetime.today() - datetime.timedelta(days=10))
#    update_start = datetime.datetime.strptime("2015-01-02",'%Y-%m-%d')
    if PRODUCTION_ENVRIONMENT:
        update_start = datetime.datetime.today() - datetime.timedelta(days = 20)
    else:
        update_start = datetime.datetime.strptime("2015-01-02",'%Y-%m-%d')
        
    update_end = datetime.datetime.today()
    number_of_days = (update_end-update_start).days
    
    for days_range in range(number_of_days):
#        days_range = 600
        date = (update_end - datetime.timedelta(days=days_range)).strftime("%Y%m%d")
        file_name_output = raw_directory+"/"+table_name+"_"+date+".xlsx"
        file_name_output_hdf = out_directory+"/"+table_name+"_"+date+".hdf"
        if os.path.exists(file_name_output) and os.path.exists(file_name_output_hdf):
            print("Already exisits/skip " + date)
            continue
        
        start_time = time.time()
        file_name_generic = date+"_"+table_name+"*.csv"
        file_name = glob.glob(file_directory+"/"+file_name_generic)
        
        if len(file_name) != 1:
            print(len(file_name))
            print("file can only be one: " + date)
            continue
            
        if not os.path.isfile(file_name[0]):
            print("file is not a file: " + date)
            print(file_name[0])
            continue
        
        data_raw = pd.read_csv(file_name[0],dtype=str)
        
        if not os.path.exists(file_name_output):
            data_raw.to_excel(file_name_output)
        else:
            print("excel exist already: " + date)
            
        if not os.path.exists(file_name_output_hdf):
            data_raw.to_hdf(file_name_output_hdf,"w",table=True)
        else:
            print("hdf exist already: " + date)

        print(table_name+"/"+"Convert data using " + str(round(time.time()-start_time,0)) + " seconds")

def UPDATE_BCBS_248_Data_Extract_A1_Report():
    table_name = "BCBS_248_Data_Extract_A1_Report"
    raw_directory = PATH_DB+table_name+"/RawData"
    out_directory = PATH_DB+table_name+"/HdfData"
    update_db_txt_BCBS_248_Data_Extract_A1_Report(table_name,raw_directory,out_directory)

def update_BCBS_248_Data_Extract_A1_Report_2016(table_name,raw_directory,out_directory):
#    date_list=["20171108"]
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    if not os.path.exists(raw_directory):
        os.makedirs(raw_directory)
    
#    update_start = (datetime.datetime.today() - datetime.timedelta(days=10))
    update_start = datetime.datetime.strptime("2016-01-04",'%Y-%m-%d')
    update_end = datetime.datetime.strptime("2016-12-31",'%Y-%m-%d')
    number_of_days = (update_end-update_start).days
    
    for days_range in range(number_of_days):
#        days_range = 362
        date = (update_end - datetime.timedelta(days=days_range)).strftime("%Y%m%d")
        file_name_output_hdf = out_directory+"/"+table_name+"_"+date+".hdf"
        if os.path.exists(file_name_output_hdf):
            print("Already exisits/skip " + date)
            continue
        
        start_time = time.time()
        file_name_generic = table_name+"_"+date+"*"
        file_name = glob.glob(raw_directory+"/"+file_name_generic)
        
        if len(file_name) != 1:
            print(len(file_name))
            print("file cannot only be one: " + date)
            continue
            
        if not os.path.isfile(file_name[0]):
            print("file is not a file: " + date)
            print(file_name[0])
            continue
        
        data_raw = pd.read_csv(file_name[0],dtype=str)

        if not os.path.exists(file_name_output_hdf):
            data_raw.iloc[:,1:].to_hdf(file_name_output_hdf,"w",table=True)
        else:
            print("hdf exist already: " + date)

        print(table_name+"/"+"Convert data using " + str(round(time.time()-start_time,0)) + " seconds")

def UPDATE_RDA_BCBS_248_Data_Extract_A1_Report_2016():
    table_name = "BCBS_248_Data_Extract_A1_Report"
    raw_directory = PATH_DB+table_name+"/RawData"
    out_directory = PATH_DB+table_name+"/HdfData"
    if not PRODUCTION_ENVRIONMENT:
        update_BCBS_248_Data_Extract_A1_Report_2016(table_name,raw_directory,out_directory)


def update_db_txt_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(table_name,raw_directory,out_directory,date_list=None):
#    date_list=["201806"]
    if date_list == None:
        print("Need to input dates")
        return()

    if not os.path.exists(out_directory):
        os.makedirs(out_directory)
    if not os.path.exists(raw_directory):
        os.makedirs(raw_directory)
    
    for date in date_list:
    #    date = date_list[0]
        file_name_source = PATH_DB+table_name+"/FTDR/"+table_name+"_"+date+".txt"
        
        if os.path.exists(file_name_source):
            print("Source File Found: "+table_name+"_"+date+".txt")
            start_time = time.time()
            
#            data_chunks = pd.read_table(file_name_source,chunksize =10**5)
            data_raw = pd.read_table(file_name_source)
#            data_raw.shape
#            data_raw.head()
#            data_raw.columns
            unique_dates = data_raw['ASOF'].drop_duplicates()
            for day in unique_dates:
#                day = unique_dates[0]
                output_date = datetime.datetime.strptime(day,"%m/%d/%Y 12:00:00 AM")
                file_name_output = raw_directory+"/"+table_name+"_"+output_date.strftime("%Y%m%d")+".xlsx"
                file_name_output_hdf = out_directory+"/"+table_name+"_"+output_date.strftime("%Y%m%d")+".hdf"
                
                if not os.path.exists(file_name_output):
                    data_raw[data_raw['ASOF'] == day].to_excel(file_name_output)
                else:
                    print("excel exist already: " + day)
                    
                if not os.path.exists(file_name_output_hdf):
                    data_raw[data_raw['ASOF'] == day].to_hdf(file_name_output_hdf,"w",table=True)
                else:
                    print("hdf exist already: " + day)

            print(table_name+"/"+"Convert data using " + str(round(time.time()-start_time,0)) + " seconds")
            
        elif not os.path.exists(file_name_source):
            print(table_name+"/"+date + ": Source File Not Found")

def UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(date_list=None):
    table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY"
    raw_directory = PATH_DB+table_name+"/RawData"
    out_directory = PATH_DB+table_name+"/HdfData"
    if date_list == None:
        print("No date is input to update table " + table_name)
        return()
        
    if date_list.__class__ == str:
        date_list = [date_list]
#    date_list = ["201806"]
#    date_list = ["201801","201802","201803","201804","201805"]
#    date_list = ["201602","201603","201604","201605","201606","201607","201608","201609","201610","201611","201612",
#     "201701","201702","201703","201704","201705","201706","201707","201708","201709","201710","201711","201712",
#     "201801","201802","201803","201804","201805"]
#    ,"201606","201607","201608","201609","201610","201611","201612",]
    update_db_txt_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(table_name,raw_directory,out_directory,date_list)

## Read data
def read_db(table_name, date_list=None):
#    date_list = today
#    date_list = formatDate(dates[table_name])
    if date_list == None:
        base = datetime.datetime.today()
        date_list = [(base - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range(0, 10)]
    elif date_list.__class__ is str:
        date_list = [date_list]

    if table_name in ["DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST","BCBS_248_Data_Extract_A1_Report",\
                      "DM_RTIM_DOM_ALL_TRANSACTION_STEP3","DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY"]:
        out_directory = PATH_DB+table_name+"/HdfData/"
        file_list = [out_directory + table_name + "_" + date + ".hdf" for date in date_list]
        data_all = read_database(file_list)
    elif table_name in ['Fed_Balance',\
                        'TRANSACTION_AMOUNT_By_CLEARING_MATERIAL_ENTITY',\
                        'TRANSACTION_AMOUNT_By_TimeBucket',\
                        'TRANSACTION_AMOUNT_By_TimeMinute',\
                        'TRANSACTION_AMOUNT_By_Time15Minute',\
                        'TRANSACTION_AMOUNT_By_Time30Minute',\
                        'TRANSACTION_AMOUNT_By_Time60Minute',\
                        'TRANSACTION_AMOUNT_By_FMU',\
                        'TRANSACTION_AMOUNT_By_SOURCEDATAMART',\
                        'TRANSACTION_AMOUNT_By_TRANSACTION_TYPE']:
        out_directory = PATH_DB+"INTRADAY_TABLES/RawData/"
        file = out_directory + table_name + ".xlsx"
        data_all = pd.ExcelFile(file).parse("Sheet1",index_col=0)
        data_all = data_all.transpose().sort_index().transpose()
    elif table_name in ['Stat_TRANSACTION_AMOUNT_By_TRANSACTION_TYPE',\
                        'Stat_TRANSACTION_AMOUNT_By_FMU',\
                        'Stat_TRANSACTION_AMOUNT_By_SOURCEDATAMART',\
                        'Stat_TRANSACTION_AMOUNT_By_TimeBucket',\
                        'TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_CLEARING_MATERIAL_ENTITY',\
                        'TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_FMU',\
                        'TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_SOURCEDATAMART',\
                        'TRANSACTION_AMOUNT_By_SOURCEDATAMART_and_FED_CHIPS_BT',\
                        'TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_TimeBucket']:
        out_directory = PATH_DB+"INTRADAY_TABLES/RawData/"
        file = out_directory + table_name + ".xlsx"
        data_all = pd.ExcelFile(file).parse("Sheet1",index_col=[1,0])
        data_all = data_all.transpose().sort_index().transpose()
    elif table_name in ['Stat_TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_FMU',\
                        'Stat_TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_CLEARING_MATERIAL_ENTITY',\
                        'Stat_TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_SOURCEDATAMART',\
                        'Stat_TRANSACTION_AMOUNT_By_TRANSACTION_TYPE_and_TimeBucket']:
        out_directory = PATH_DB+"INTRADAY_TABLES/RawData/"
        file = out_directory + table_name + ".xlsx"
        data_all = pd.ExcelFile(file).parse("Sheet1",index_col=[2,1,0])
        data_all = data_all.transpose().sort_index().transpose()
    elif table_name in ['RUNNINGTOTAL_TRANSACTION_AMOUNT','RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT','RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT',"RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_15min","RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_15min",\
                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_with_FedBalance','RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_with_FedBalance','RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_with_FedBalance',\
                        'IL_RUNNINGTOTAL_TRANSACTION_AMOUNT','IL_RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT','IL_RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT']:
        data_all = read_database(misc_dir+"/HdfData/"+table_name+".hdf")
#    elif table_name in ['RUNNINGTOTAL_TRANSACTION_AMOUNT_STT-Total',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_SSBT BOSTON',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_SSBT NEW YORK',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CHIPS',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_Fedwire Funds',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_Fedwire Securities',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_FED CHK',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_FED ACH',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DTCC - FICC',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_STT-Total',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_SSBT BOSTON',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_SSBT NEW YORK',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_CHIPS',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_Fedwire Funds',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_Fedwire Securities',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_FED CHK',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_FED ACH',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_DTCC - FICC',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_STT-Total',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_SSBT BOSTON',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_SSBT NEW YORK',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_CHIPS',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_Fedwire Funds',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_Fedwire Securities',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_FED CHK',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_FED ACH',\
#                        'RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_DTCC - FICC']:
#        data_all = read_database(misc_dir+"/HdfData/"+table_name+".hdf")
#        data_all.index = [datetime.datetime.strptime(x, "%H:%M:%S").time() for x in data_all.index]
    elif table_name.startswith('RUNNINGTOTAL_TRANSACTION_AMOUNT'):
        out_directory = PATH_DB+"INTRADAY_TABLES/RawData/"
        file = out_directory + table_name + ".xlsx"
        data_all = pd.ExcelFile(file).parse("Sheet1",index_col=0)
        data_all = data_all.transpose().sort_index().transpose()
    elif table_name.startswith('IL_RUNNINGTOTAL_TRANSACTION_AMOUNT'):
        out_directory = PATH_DB+"INTRADAY_TABLES/RawData/"
        file = out_directory + table_name + ".xlsx"
        data_all = pd.ExcelFile(file).parse("Sheet1",index_col=0)
        data_all = data_all.transpose().sort_index().transpose()
    else:
        print("Cannot find the database. Check table name " + table_name)
        return()
    
    return(data_all)

#table_name = 'IL_RUNNINGTOTAL_TRANSACTION_AMOUNT_EUR'
    
