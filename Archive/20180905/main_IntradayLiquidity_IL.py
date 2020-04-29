# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 16:01:25 2017
Analyze treasury common deposits file
@author: e620927
"""

PRODUCTION_ENVRIONMENT = True

import datetime
################# Global Parameters  #################
if PRODUCTION_ENVRIONMENT:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes-Production"
    output_dir = "Z:/Charles/IntradayLiquidity/Output_IL"
    pdf_dir = "Z:/Charles/IntradayLiquidity/PDFReport_IL"
    TEST_ENVIRONMENT = False
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=1)
else:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"
    output_dir = "Z:/Charles/IntradayLiquidity/Output_IL_Test"
    pdf_dir = "Z:/Charles/IntradayLiquidity/PDFReport_IL_Test"
    TEST_ENVIRONMENT = True

#Setup parameters
if TEST_ENVIRONMENT:
    start_date = datetime.datetime.strptime('2018-08-03 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
    end_date = datetime.datetime.strptime('2018-08-03 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2017-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2017-12-31 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2017-11-01 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2017-11-30 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2017-10-01 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2017-10-31 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2017-09-01 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2017-09-30 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2017-08-01 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2017-08-31 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2017-07-01 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2017-07-31 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    timewindow = [(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range((end_date-start_date).days+1)]

    timewindow = [(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range((end_date-start_date).days+1)]
#    timewindows = [[(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d")] for x in range((end_date-start_date).days+1)]

################# Global Libraries #################
import os
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})
from matplotlib.ticker import FuncFormatter
import subprocess
import imp
import matplotlib.transforms as mtransforms

################# Local Libraries #################
os.chdir(code_dir)
# Load local functions
import UpdateDatabase_Intraday_DB_IL
imp.reload(UpdateDatabase_Intraday_DB_IL)
from UpdateDatabase_Intraday_DB_IL import read_db, update_daily_tables
import process_IntradayLiquidity_IL
imp.reload(process_IntradayLiquidity_IL)
from process_IntradayLiquidity_IL import update_table1, update_table3, update_table4
import Functions_Analysis
imp.reload(Functions_Analysis)
from Functions_Analysis import process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST, create_unique_dirname

update_daily_tables()

if PRODUCTION_ENVRIONMENT:
    update_table1()
    update_table3()
    update_table4()
    timewindows = [[max(read_db("IL_DER_TRANSACTION_AMOUNT_USD_By_FMU_and_TRANSACTION_TYPE_and_ACCOUNT_TYPE_and_CURRENCY_CODE").columns[4:])]]

# create folder hierarchy
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)
    
day = datetime.date.today().strftime("%Y%m%d")
plot_folder = output_dir+"/Output_"+day
plot_folder = create_unique_dirname(plot_folder)

if not os.path.exists(plot_folder):
    os.mkdir(plot_folder)

################# formats and styles #################
pd.options.mode.chained_assignment = None
plt.style.use('ggplot')
styles = ['b-','g-','r-','c-','m-','y-','k-']
styles2 = ['b--','g--','r--','c--','m--','y--','k--']

def percentages(x):
    return '{:.1%}'.format(x)
def millions(x, pos=0):
    return '{:,.1f}M'.format(x*1e-6)
def millionsinteger(x, pos=0):
    return '{:,.0f}M'.format(x*1e-6)
def billions(x, pos=0):
    return '{:,.1f}B'.format(x*1e-9)
def billionsinteger(x, pos=0):
    return '{:,.0f}B'.format(x*1e-9)

formatter_percentages = FuncFormatter('{0:.0%}'.format)
formatter_millions = FuncFormatter(millions)
formatter_millionsinteger = FuncFormatter(millionsinteger)
formatter_billions = FuncFormatter(billions)
formatter_billionsinteger = FuncFormatter(billionsinteger)

#################### Finish Configuration ####################

#################### Start Analysis ####################
start_time = time.time()

#new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME"
column_name_transaction_amount = "DER_TRANSACTION_AMOUNT_USD"
column_name_transaction_type = "TRANSACTION_TYPE"
column_name_legal_entity = "MATERIAL_ENTITY"
column_name_datamart = "SOURCEDATAMART"
column_name_currency = "CURRENCY_CODE"
column_name_account_type = "ACCOUNT_TYPE"
column_name_agent_bank_name = "AGENT_BANK_NAME"
column_name_fmu = "FMU"
column_name_running_total = "RUNNING_TOTAL"

column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"
column_name_15minutes = "Time15Minute"
column_name_30minutes = "Time30Minute"
column_name_60minutes = "Time60Minute"

#LNNCP threshold
limit_yellow_withfed = 5E9
limit_red_withfed = 3E9
limit_red_nofed = -11.9E9

def consolidate_columns(df):
#    df = summary_tmp.copy()
    if not len(df.columns.drop_duplicates()) < len(df.columns):
        return(df)
    else:
        df_new=pd.DataFrame()
        for column_name in df:
            df_new[column_name] = df[[column_name]].apply(np.nansum,axis=1)
        return(df_new)

def aggregate_other(df_tmp):
#    df_tmp = summary_tmp.copy()
    if df_tmp.shape[1] > 7:
        ranked_labels = df_tmp.apply(np.nansum,axis=0).sort_values(ascending=False).index
        largest_ones = ranked_labels[:7]
        others = ranked_labels[7:]
        df_return = df_tmp[largest_ones].copy()
        df_return["Others"]=df_tmp[others].apply(np.nansum,axis=1)
        return(df_return)

for timewindow in timewindows:
    #################### Process Horizontal Data #########
    ####Currency percentage
    #
    #balance_type = column_name_transaction_amount
    #attribute_groupby = [column_name_fmu,column_name_transaction_type,column_name_account_type,column_name_currency]
    #table_name = "IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)
    #summary_data = read_db(table_name)
    #summary_data[column_name_fmu] = summary_data[column_name_fmu].fillna("Not Identified")
    #
    #select_column = column_name_currency
    #summary_tmp = summary_data[(summary_data[column_name_transaction_type]=="DEBIT")] #&(summary_data[column_name_account_type].isin(["PRI","DPP"]))
    #summary_tmp = summary_tmp.drop(list(set(attribute_groupby)-set([select_column])),axis=1)
    #summary_tmp = summary_tmp.set_index(select_column).fillna(0)
    #summary_tmp.columns = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_tmp.columns]
    #summary_tmp = summary_tmp.transpose().sort_index()
    #
    #summary_tmp = consolidate_columns(summary_tmp)
    #summary_tmp = aggregate_other(summary_tmp)
    #plt.figure()
    #figure = summary_tmp.plot(style=styles,linewidth=1.3)
    #figure.yaxis.set_major_formatter(formatter_billionsinteger)
    #figure.xaxis.label.set_visible(False)
    #plt.title("Daily Debit Payments by " + select_column,fontsize=20)
    #plt.legend(loc="best",prop={'size':10})
    ##        plt.rcParams.update({'font.size': 12})
    #fig = figure.get_figure()
    #fig.set_size_inches(10, 8)
    #fig.savefig(plot_folder+"/History_Chart_Daily_Debit_Payments_by_" +select_column +".png",bbox_inches='tight')
    #summary_tmp.to_excel(plot_folder+"/History_Chart_Daily_Debit_Payments_by_" +select_column +".xlsx")
    #
    #plt.figure()
    #figure = summary_tmp.div(summary_tmp.apply(np.nansum,axis=1),axis=0).plot(style=styles,linewidth=1.3)
    #figure.yaxis.set_major_formatter(formatter_percentages)
    #figure.xaxis.label.set_visible(False)
    #plt.title("Daily Debit Payments by " + select_column + " in % terms",fontsize=20)
    #plt.legend(loc="best",prop={'size':10})
    ##        plt.rcParams.update({'font.size': 12})
    #fig = figure.get_figure()
    #fig.set_size_inches(10, 8)
    #fig.savefig(plot_folder+"/History_Chart_Daily_Debit_Payments_by_" +select_column +"_Percentage.png",bbox_inches='tight')
    #summary_tmp.div(summary_tmp.apply(np.nansum,axis=1),axis=0).to_excel(plot_folder+"/History_Chart_Daily_Debit_Payments_by_" +select_column +"_Percentage.xlsx")
    #
    #Currencies = ["EUR","JPY","CAD","GBP"]
    #for currency in Currencies:
    ##    currency = "EUR"
    #    summary_tmp = summary_data[(summary_data[column_name_currency] == currency)&(summary_data[column_name_transaction_type]=="DEBIT")] #&(summary_data[column_name_account_type].isin(["PRI","DPP"]))
    #    summary_tmp = summary_tmp.set_index(column_name_fmu)
    #    del(summary_tmp[column_name_transaction_type])
    #    del(summary_tmp[column_name_currency])
    #    summary_tmp.columns = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_tmp.columns]
    #    summary_tmp = summary_tmp.transpose().sort_index()
    #    
    #    summary_tmp = consolidate_columns(summary_tmp)
    #
    #    plt.figure()
    #    figure = (-1*summary_tmp).plot(style=styles,linewidth=1.3)
    #    figure.yaxis.set_major_formatter(formatter_billionsinteger)
    #    figure.xaxis.label.set_visible(False)
    #    plt.title("Daily "+currency+" Debit Payments by FMU",fontsize=20)
    #    plt.legend(loc="best",prop={'size':10})
    #    #        plt.rcParams.update({'font.size': 12})
    #    fig = figure.get_figure()
    #    fig.set_size_inches(10, 8)
    #    fig.savefig(plot_folder+"/History_Chart_Daily_"+currency+"_Debit_Payments_by_FMU.png",bbox_inches='tight')
    #
    #    plt.figure()
    #    figure = summary_tmp.div(summary_tmp.apply(np.nansum,axis=1),axis=0).plot(style=styles,linewidth=1.3)
    #    figure.yaxis.set_major_formatter(formatter_percentages)
    #    figure.xaxis.label.set_visible(False)
    #    plt.title("Daily "+currency+" Debit Payments by FMU in % terms",fontsize=20)
    #    plt.legend(loc="best",prop={'size':10})
    #    #        plt.rcParams.update({'font.size': 12})
    #    fig = figure.get_figure()
    #    fig.set_size_inches(10, 8)
    #    fig.savefig(plot_folder+"/History_Chart_Daily_"+currency+"_Debit_Payments_by_FMU_Percentage.png",bbox_inches='tight')
    
    
    
    
    balance_type = column_name_transaction_amount
    
    ##STT Corp
    #attribute_groupby = [column_name_transaction_type]
    #table_name = balance_type+"_By_"+ "_and_".join(attribute_groupby)
    #
    #summary_data = read_db(table_name)
    #if len(summary_data) == 0:
    #    exit("No file found for " + table_name)
    #
    #summary_data = summary_data.transpose()
    #summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    #
    #data_plot = summary_data
    #data_plot = data_plot[["CREDIT","DEBIT"]]
    #data_plot['Net'] = data_plot['CREDIT'] + data_plot['DEBIT'] 
    #
    #data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
    #plt.figure()
    #figure = data_plot.plot(style=styles,linewidth=1.3)
    #figure.yaxis.set_major_formatter(formatter_billionsinteger)
    #figure.xaxis.label.set_visible(False)
    #plt.title("Daily Credit/Debit Payments for STT Corp in USD Billions\n(Average in Parentheses)",fontsize=20)
    #plt.legend(loc="best",prop={'size':10})
    ##        plt.rcParams.update({'font.size': 12})
    #fig = figure.get_figure()
    #fig.set_size_inches(10, 8)
    #fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_STT_Corp.png",bbox_inches='tight')
    #
    ##By LE and FMUs
    #attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_currency]
    #for attribute in attributes:
    ##    attribute = column_name_legal_entity
    #    #attribute = column_name_hour
    #    #attribute = column_name_fmu
    ##    attribute_groupby = [column_name_transaction_type]
    #    attribute_groupby = [column_name_transaction_type, attribute]
    ##    attribute_groupby = [column_name_transaction_type, attribute]
    #
    #    table_name = balance_type+"_By_"+ "_and_".join(attribute_groupby)
    #    
    #    summary_data = read_db(table_name)
    #    if len(summary_data) == 0:
    #        continue
    #    
    #    summary_data = summary_data.transpose()
    #    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    #    
    #    sub_categorys = summary_data.columns.get_level_values(attribute).drop_duplicates().tolist()
    #    for sub_category in sub_categorys:
    ##        sub_category = 'SSBT BOSTON'
    ##        sub_category = 'SSBT NEW YORK'
    #        
    #        data_plot = summary_data[sub_category]
    #        if not any(data_plot.columns=="CREDIT")&any(data_plot.columns=="DEBIT"):
    #            continue
    #        data_plot = data_plot[["CREDIT","DEBIT"]]
    #        data_plot['Net'] = data_plot['CREDIT'] + data_plot['DEBIT'] 
    #
    #        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
    #        plt.figure()
    #        figure = data_plot.plot(style=styles,linewidth=1.3)
    #        figure.yaxis.set_major_formatter(formatter_billionsinteger)
    #        figure.xaxis.label.set_visible(False)
    #        plt.title("Daily Credit/Debit Payments for "+sub_category+" in USD Billions\n(Average in Parentheses)",fontsize=20)
    #        plt.legend(loc='best',prop={'size':10})
    ##        plt.rcParams.update({'font.size': 12})
    #        fig = figure.get_figure()
    #        fig.set_size_inches(10, 8)
    #        fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
    #    
    #### Stat
    #attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_fmu,column_name_transaction_type]
    #for attribute in attributes:
    ##    attribute = column_name_fmu
    ##    attribute = column_name_hour
    #
    #    attribute_groupby = [column_name_transaction_type,attribute]
    #    table_name = 'Stat_'+balance_type+"_By_"+ "_and_".join(attribute_groupby)
    #    
    #    summary_data = read_db(table_name)
    #    if len(summary_data) == 0:
    #        continue
    #    summary_data = summary_data.transpose()
    #    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    #    sub_categories = summary_data.columns.get_level_values(attribute).drop_duplicates().tolist()
    #    
    #    for sub_category in sub_categories:
    #        #    sub_category = sub_categories[5]
    #        
    #        data_plot = summary_data[sub_category]['CREDIT']
    ##        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(formatter_millions))]
    #        plt.figure()
    #        figure = data_plot.loc[:,['maximum','percentile_99','percentile_95','std','average','percentile_5','percentile_1','minimum']].plot(style=styles,linewidth=1.3)
    #        figure.yaxis.set_major_formatter(formatter_millionsinteger)
    #        figure.xaxis.label.set_visible(False)
    #        plt.title("Statistics For "+ sub_category+"'s Credit Transactions in USD Millions",fontsize=20)
    #        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
    ##        plt.legend(loc='best',prop={'size':10})
    ##        plt.rcParams.update({'font.size': 20})
    #        fig = figure.get_figure()
    #        fig.set_size_inches(10, 8)
    #        fig.savefig(plot_folder+"/Statistics_By_TotalCreditPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
    #
    #        data_plot = summary_data[sub_category]['DEBIT']
    ##        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(formatter_millions))]
    #        plt.figure()
    #        figure = data_plot.loc[:,['maximum','percentile_99','percentile_95','std','average','percentile_5','percentile_1','minimum']].plot(style=styles,linewidth=1.3)
    #        figure.yaxis.set_major_formatter(formatter_millionsinteger)
    #        figure.xaxis.label.set_visible(False)
    #        plt.title("Statistics For "+ sub_category+"'s Debit Transactions in USD Millions",fontsize=20)
    #        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
    ##        plt.rcParams.update({'font.size': 12})
    #        fig = figure.get_figure()
    #        fig.set_size_inches(10, 8)
    #        fig.savefig(plot_folder+"/Statistics_By_TotalDEBITPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
    
    ## Analyze running total
    Running = read_db("IL_RUNNINGTOTAL_"+balance_type)
    ##Running.shape
    ##Running.index
    ##Running.head()
    ##Running.fillna()
    ##Running['STT-Total'].plot()
    #def extract_lnncp(running_tmp):
    #    if all(np.isnan(running_tmp)):
    #        return(np.nan)
    #    lnncp = min(running_tmp)
    #    return(lnncp)
    #def extract_lnncp_time(running_tmp):
    #    if all(np.isnan(running_tmp)):
    #        return(np.nan)
    #    lnncp = min(running_tmp)
    #    lnncp_time = running_tmp[running_tmp == lnncp].index[0]
    #    return(lnncp_time)
    #def extract_lpncp(running_tmp):
    #    if all(np.isnan(running_tmp)):
    #        return(np.nan)
    #    lpncp = max(running_tmp)
    #    return(lpncp)
    #def extract_lpncp_time(running_tmp):
    #    if all(np.isnan(running_tmp)):
    #        return(np.nan)
    #    lpncp = max(running_tmp)
    #    lpncp_time = running_tmp[running_tmp == lpncp].index[0]
    #    return(lpncp_time)
    #    
    #sub_categories = Running.columns
    #for sub_category in sub_categories:
    ##    sub_category = 'STT-Total'
    #    result_tmp = Running[sub_category].resample('1D').apply([extract_lnncp,extract_lnncp_time,extract_lpncp,extract_lpncp_time])
    #    result_tmp = result_tmp.dropna()
    #    
    #    result_tmp.columns = ['LNNCP','LNNCP_Time','LPNCP','LPNCP_Time']
    #    
    #    stat_type = 'LPNCP'
    #    p50 = np.nanpercentile(result_tmp[[stat_type]],50)
    #    p75 = np.nanpercentile(result_tmp[[stat_type]],75)
    #    p95 = np.nanpercentile(result_tmp[[stat_type]],95)
    #
    #    fig, ax = plt.subplots()
    #    result_tmp[[stat_type]].dropna().plot(ax=ax,style=styles)
    #    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    #    ax.axhline(y=p50,linewidth=2,zorder=0,color='y')
    #    ax.axhline(y=p75,linewidth=2,zorder=0,color='m')
    #    ax.axhline(y=p95,linewidth=2,zorder=0,color='g')
    #    ax.yaxis.set_major_formatter(formatter_billions)
    #    ax.tick_params(labelsize=20)
    #    ax.xaxis.label.set_visible(False)
    #    ax.set_title("Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 75th and 95th Percentiles",fontsize=20)
    #    fig.set_size_inches(12,9)
    #    fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
    #    plt.clf()
    #        
    #    lnncp_time = [x.time() for x in result_tmp[stat_type+'_Time']]
    #    fig, ax = plt.subplots()
    #    ax.plot_date(result_tmp.index,lnncp_time)
    #    ax.xaxis.label.set_visible(False)
    #    ax.set_title("Timing of "+stat_type + " for " + sub_category,fontsize=20)
    #    fig.set_size_inches(12,9)
    #    fig.savefig(plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_"+stat_type+"_Timing.png",bbox_inches='tight')
    #    plt.clf()
    #        
    #    stat_type = 'LNNCP'
    #    p50 = np.nanpercentile(result_tmp[[stat_type]],50)
    #    p25 = np.nanpercentile(result_tmp[[stat_type]],25)
    #    p5 = np.nanpercentile(result_tmp[[stat_type]],5)
    #
    #    fig, ax = plt.subplots()
    #    result_tmp[[stat_type]].dropna().plot(ax=ax,style=styles)
    #    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    #    ax.axhline(y=p50,linewidth=2,zorder=0,color='y')
    #    ax.axhline(y=p25,linewidth=2,zorder=0,color='m')
    #    ax.axhline(y=p5,linewidth=2,zorder=0,color='g')
    #    ax.yaxis.set_major_formatter(formatter_billions)
    #    ax.tick_params(labelsize=20)
    #    ax.xaxis.label.set_visible(False)
    #    ax.set_title("Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 25th and 5th Percentiles",fontsize=20)
    #    fig.set_size_inches(12,9)
    #    fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
    #    plt.clf()
    #        
    #    lnncp_time = [x.time() for x in result_tmp[stat_type+'_Time']]
    #    fig, ax = plt.subplots()
    #    ax.plot_date(result_tmp.index,lnncp_time)
    #    ax.xaxis.label.set_visible(False)
    #    ax.set_title("Timing of "+stat_type + " for " + sub_category,fontsize=20)
    #    fig.set_size_inches(12,9)
    #    fig.savefig(plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_"+stat_type+"_Timing.png",bbox_inches='tight')
    #    plt.clf()
    
    #################### Analyze specific day's data #########
    #plot with and without beginning balance
    
    def analyze_intraday_data(tmp_data,file_suffix,key,limit_red_nofed = None, fed_balance = None):
    #        tmp_data = data_tmp[data_tmp["FMU"]==fmu]
    #          file_suffix = fmu.replace(" ", "")
    #        tmp_data = data_tmp[data_tmp["CLEARING_MATERIAL_ENTITY"]==le]
    #        tmp_data = data_tmp
    #    file_suffix = "ALL_US_Transactions"
        #key = fmu
    #    fed_balance = Fed_balance.loc[date,'Fed_Balance']
        if len(tmp_data) == 0:
            return()
        
        ###transaction-level analysis
        # largest 10-25 transactons, when who
    #    top_number = 25
    #    threshold = tmp_data[column_name_transaction_amount].sort_values(ascending=False)[top_number]
    #    
    #    if column_name_running_total in tmp_data.columns:
    #        result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] > threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,column_name_running_total,column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
    #    else:
    #        result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] > threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,'CALC_RUNNING_TOTAL',column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
    #        
    #    result_largest_transaction.sort_values(by=[column_name_transaction_amount],ascending=False,inplace=True)
    #    result_largest_transaction.sort_values(by=[column_name_hour],ascending=True,inplace=True)
    #    result_largest_transaction.columns = ['Time', 'TimeBucket', 'Amount', 'RunningTot','Type','FMU','FedAccount']
    #    result_largest_transaction[['Amount','RunningTot']] = result_largest_transaction[['Amount','RunningTot']].applymap(billions)
    #    result_largest_transaction.index = range(1,result_largest_transaction.shape[0]+1)
    #    file_name = plot_folder+"/IntradayLiquidity_largest_credit_transactions_"+date+"_"+file_suffix+".tex"
    #    result_largest_transaction.to_latex(file_name,longtable=True)
    #    
    #    threshold = tmp_data[column_name_transaction_amount].sort_values(ascending=True)[top_number]
    #    if column_name_running_total in tmp_data.columns:
    #        result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] < threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,column_name_running_total,column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
    #    else:
    #        result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] < threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,'CALC_RUNNING_TOTAL',column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
    #        
    #    result_largest_transaction.sort_values(by=[column_name_transaction_amount],ascending=True,inplace=True)
    #    result_largest_transaction.sort_values(by=[column_name_hour],ascending=True,inplace=True)
    #
    #    result_largest_transaction.columns = ['Time', 'TimeBucket', 'Amount', 'RunningTot','Type','FMU','FedAccount']
    #    result_largest_transaction[['Amount','RunningTot']] = result_largest_transaction[['Amount','RunningTot']].applymap(billions)
    #    result_largest_transaction.index = range(1,result_largest_transaction.shape[0]+1)
    #    file_name = plot_folder+"/IntradayLiquidity_largest_debit_transactions_"+date+"_"+file_suffix+".tex"
    #    result_largest_transaction.to_latex(file_name,longtable=True)
        
        ###Running total analysis
        data_tmp_nobalance = tmp_data.groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
        data_tmp_nobalance[column_name_running_total] = data_tmp_nobalance[column_name_transaction_amount].cumsum()
    
        lnncp = min(data_tmp_nobalance[column_name_running_total])
        lpncp = max(data_tmp_nobalance[column_name_running_total])
        
        lnncp_time = data_tmp_nobalance[data_tmp_nobalance[column_name_running_total] == lnncp].index[0]
        lpncp_time = data_tmp_nobalance[data_tmp_nobalance[column_name_running_total] == lpncp].index[0]
        
        fig, ax = plt.subplots()
        data_tmp_nobalance[column_name_running_total].dropna().plot(ax=ax,style=styles)
        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    #    if limit_red_nofed is not None:
    #        ax.fill_between(data_tmp_nobalance[column_name_running_total].index, 0, 1, where=data_tmp_nobalance[column_name_running_total] < limit_red_nofed, facecolor='red', alpha=0.5, transform=trans)
    #        ax.axhline(y=limit_red_nofed,linewidth=2,zorder=0,color='red')
    #        ax.text(0.1, 0.1,'Red Limit: '+str(formatter_billions(limit_red_nofed)),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
        ax.axhline(y=lnncp,linewidth=2,zorder=0,color='mediumvioletred')
        ax.text(0.85, 0.9,"LPNCP: " + str(round(lpncp/1e9,1))  + "/Time: "+ lpncp_time.strftime("%H:%M"),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
        ax.text(0.85, 0.1,"LNNCP: " + str(round(lnncp/1e9,1)) + "/Time: "+ lnncp_time.strftime("%H:%M") ,horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
        ax.yaxis.set_major_formatter(formatter_billions)
        ax.tick_params(labelsize=15)
        custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
        plt.xticks(custom_tick_locs,rotation=90)
        ax.xaxis.label.set_visible(False)
        ax.set_title("Running Total Balance "+date+": " + file_suffix,fontsize=20)
        fig.set_size_inches(12,9)
        fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()
        
        if fed_balance is not None:
            fig, ax = plt.subplots()
            data_tmp_nobalance[column_name_running_total].add(fed_balance).dropna().plot(ax=ax,style=styles)
            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
            ax.fill_between(data_tmp_nobalance[column_name_running_total].index, 0, 1, where=data_tmp_nobalance[column_name_running_total].add(fed_balance) < limit_red_withfed, facecolor='red', alpha=0.5, transform=trans)
            ax.fill_between(data_tmp_nobalance[column_name_running_total].index, 0, 1, where=data_tmp_nobalance[column_name_running_total].add(fed_balance) < limit_yellow_withfed, facecolor='orange', alpha=0.5, transform=trans)
            ax.axhline(y=limit_yellow_withfed,linewidth=2,zorder=0,color='orange')
            ax.axhline(y=limit_red_withfed,linewidth=2,zorder=0,color='red')
            ax.text(0.1, 0.1,'Red Limit: '+str(formatter_billions(limit_red_withfed))+'\nYellow Limit: '+str(formatter_billions(limit_yellow_withfed)),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
            ax.yaxis.set_major_formatter(formatter_billions)
            ax.tick_params(labelsize=15)
            custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
            plt.xticks(custom_tick_locs,rotation=90)
            ax.xaxis.label.set_visible(False)
            ax.set_title("Running Total Balance with Fed Balance "+date+": " + file_suffix,fontsize=20)
            fig.set_size_inches(12,9)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+".png",bbox_inches='tight')
            plt.clf()
        
        ## with corridor
        table_name = "IL_RUNNINGTOTAL_"+column_name_transaction_amount+"_"+key
        percentiles_runningtotal = read_db(table_name)
        percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
        red_corridor = '5th Percentile'
        yellow_corridor = '25th Percentile'
        data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].join(percentiles_runningtotal)
        
        if len(percentiles_runningtotal) >0:
            fig, ax = plt.subplots()
            data_tmp_nobalance_with_corridor[column_name_running_total].dropna().plot(ax=ax,color="black",linewidth=2)
#            data_tmp_nobalance_with_corridor.iloc[:,1:].plot(ax=ax,style=styles2,alpha=0.5)
            percentiles_runningtotal.dropna().plot(ax=ax,style=styles2,alpha=0.5)
            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
            ax.fill_between(data_tmp_nobalance_with_corridor[column_name_running_total].index, 0, 1, where=data_tmp_nobalance_with_corridor[column_name_running_total] < data_tmp_nobalance_with_corridor[red_corridor], facecolor='red', alpha=0.5, transform=trans)
            ax.tick_params(labelsize=15)
            plt.xticks(custom_tick_locs,rotation=90)
            ax.xaxis.label.set_visible(False)
            ax.set_title("Running Total Balance "+date+" with Percentiles: " + file_suffix,fontsize=20)
            ax.yaxis.set_major_formatter(formatter_billions)
            fig.set_size_inches(12,9)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
            plt.clf()
            data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+"_with_corridor.xlsx")
     
        if fed_balance is not None:
            table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_with_FedBalance_"+key
            percentiles_runningtotal = read_db(table_name)
            percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
            data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].add(fed_balance).join(percentiles_runningtotal)
    
            if len(percentiles_runningtotal) >0:
                fig, ax = plt.subplots()
    #                ax.yaxis.set_major_formatter(formatter_billions)
                data_tmp_nobalance_with_corridor[column_name_running_total].dropna().plot(ax=ax,color="black",linewidth=2)
                percentiles_runningtotal.dropna().plot(ax=ax,style=styles2,alpha=0.5)
                trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
                ax.fill_between(data_tmp_nobalance_with_corridor[column_name_running_total].index, 0, 1, where=data_tmp_nobalance_with_corridor[column_name_running_total] < data_tmp_nobalance_with_corridor[yellow_corridor], facecolor='orange', alpha=0.5, transform=trans)
                ax.fill_between(data_tmp_nobalance_with_corridor[column_name_running_total].index, 0, 1, where=data_tmp_nobalance_with_corridor[column_name_running_total] < data_tmp_nobalance_with_corridor[red_corridor], facecolor='red', alpha=0.5, transform=trans)
                ax.tick_params(labelsize=15)
                plt.xticks(custom_tick_locs,rotation=90)
                ax.xaxis.label.set_visible(False)
                ax.set_title("Running Total Balance "+date+" with Percentiles: " + file_suffix,fontsize=20)
                fig.set_size_inches(12,9)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
                plt.clf()
    
        #through put graphs
        data_tmp_credit = tmp_data[tmp_data[column_name_transaction_type] == "CREDIT"].groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
        data_tmp_debit = tmp_data[tmp_data[column_name_transaction_type] == "DEBIT"].groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
        data_tmp_credit[column_name_running_total] = data_tmp_credit[column_name_transaction_amount].cumsum()
        data_tmp_debit[column_name_running_total] = data_tmp_debit[column_name_transaction_amount].cumsum()
        
        throughput_credit = data_tmp_credit[column_name_running_total]/max(data_tmp_credit[column_name_running_total])
        throughput_debit = data_tmp_debit[column_name_running_total]/min(data_tmp_debit[column_name_running_total])
        
        #abosolute amount: combined
        fig, ax = plt.subplots()
        data_tmp_credit[column_name_running_total].plot(ax=ax,style=styles[0])
        (-1*data_tmp_debit[column_name_running_total]).plot(ax=ax,style=styles[1])
        ax.yaxis.set_major_formatter(formatter_billions)
        ax.tick_params(labelsize=20)
        ax.xaxis.label.set_visible(False)
        ax.set_title("Throughput Analysis "+date+": " + file_suffix,fontsize=15)
        labels = ["Credit Throughput", "Debit Throughput"]
        lines, _ = ax.get_legend_handles_labels()
        ax.legend(lines, labels, loc='best')
        plt.xticks(custom_tick_locs,rotation=90)
        fig.set_size_inches(12,9)
        fig.savefig(plot_folder+"/IntradayLiquidity_throughput_amount_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()
        
        #abosolute amount: credit
    #    table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_"+key
    ##        table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_15min"
    #    
    #    percentiles_runningtotal = read_db(table_name)
    #
    #    if len(percentiles_runningtotal) >0:
    #        percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
    #        data_tmp_combined = data_tmp_credit[[column_name_running_total]].join(percentiles_runningtotal,how="left")
    #        fig, ax = plt.subplots()
    #        data_tmp_combined[column_name_running_total].plot(ax=ax,style=styles[0])
    #        percentiles_runningtotal.dropna().plot(ax=ax,style=styles2,alpha=0.5)
    ##        data_tmp_combined.iloc[:,1:].plot(ax=ax,style=styles2,alpha=0.5)
    ##        ax.fill_between(data_tmp_combined[column_name_running_total].index, -1, 1, where=data_tmp_combined['RUNNING_TOTAL'] < data_tmp_combined['5th Percentile'], facecolor='red', alpha=0.5, transform=trans)
    ##        ax.fill_between(data_tmp_combined[column_name_running_total].index, -1, 1, where=data_tmp_combined['RUNNING_TOTAL'] < data_tmp_combined['25th Percentile'], facecolor='yellow', alpha=0.5, transform=trans)
    #        ax.yaxis.set_major_formatter(formatter_billions)
    #        ax.tick_params(labelsize=20)
    #        ax.xaxis.label.set_visible(False)
    ##        ax.set_title("Throughput Analysis for Credit Transactions for "+file_suffix +": "+date+"\n Yellow Zone: below 25th Perc. Red Zone: below 5th Perc.",fontsize=15)
    #        ax.set_title("Throughput Analysis for Credit Transactions for "+file_suffix +": "+date,fontsize=15)
    #        labels = ["Credit Throughput"] + percentiles_runningtotal.columns.tolist()
    #        lines, _ = ax.get_legend_handles_labels()
    #        ax.legend(lines, labels, loc='best')
    #        plt.xticks(custom_tick_locs,rotation=90)
    #        fig.set_size_inches(12,9)
    #        fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_credit_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
    #        plt.clf()
    #
    #    #abosolute amount: debit
    #    table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_"+key
    ##        table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_15min_"+key
    #    
    #    percentiles_runningtotal = read_db(table_name)
    #
    #    if len(percentiles_runningtotal) >0:
    #        percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
    #        data_tmp_combined = data_tmp_debit[[column_name_running_total]].join(percentiles_runningtotal,how="left")
    ##        data_tmp_combined.to_excel(plot_folder+"/test.xlsx")
    ##        fig, ax = plt.subplots()
    ##        data_tmp_combined[column_name_running_total].plot(ax=ax,style=styles[0])
    ##        data_tmp_combined.iloc[:,1:].plot(ax=ax,style=styles2,alpha=0.5)
    ##        ax.fill_between(data_tmp_combined[column_name_running_total].index, -1, 1, where=data_tmp_combined['RUNNING_TOTAL'] < data_tmp_combined['5th Percentile'], facecolor='red', alpha=0.5, transform=trans)
    ##        ax.fill_between(data_tmp_combined[column_name_running_total].index, -1, 1, where=data_tmp_combined['RUNNING_TOTAL'] < data_tmp_combined['25th Percentile'], facecolor='yellow', alpha=0.5, transform=trans)
    #
    #        fig, ax = plt.subplots()
    #        (-1*data_tmp_debit[column_name_running_total]).plot(ax=ax,style=styles[1])
    #        (-1*percentiles_runningtotal.dropna()).plot(ax=ax,style=styles2,alpha=0.5)
    #        ax.yaxis.set_major_formatter(formatter_billions)
    #        ax.tick_params(labelsize=20)
    #        ax.xaxis.label.set_visible(False)
    #        ax.set_title("Throughput Analysis for Debit Transactions for "+file_suffix +": "+date,fontsize=15)
    #        labels = ["Debit Throughput"]+ percentiles_runningtotal.columns.tolist()
    #        lines, _ = ax.get_legend_handles_labels()
    #        ax.legend(lines, labels, loc='best')
    #        plt.xticks(custom_tick_locs,rotation=90)
    #        fig.set_size_inches(12,9)
    #        fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_debit_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
    #        plt.clf()
    #    
        #percentage term: combined
        fig, ax = plt.subplots()
        throughput_credit.plot(ax=ax,style=styles[0])
        throughput_debit.plot(ax=ax,style=styles[1])
        ax.yaxis.set_major_formatter(formatter_percentages)
        ax.tick_params(labelsize=20)
        ax.xaxis.label.set_visible(False)
        ax.set_title("Throughput Analysis "+date+": " + file_suffix,fontsize=15)
        labels = ["Credit Throughput", "Debit Throughput"]
        lines, _ = ax.get_legend_handles_labels()
        ax.legend(lines, labels, loc='best')
        fig.set_size_inches(12,9)
        plt.xticks(custom_tick_locs,rotation=90)
        fig.savefig(plot_folder+"/IntradayLiquidity_throughput_percentage_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()
        
    table_name = "DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST"
    AsOfDates = []
    for date in timewindow:
    #    date = timewindow[1]
        data_tmp = read_db(table_name,date)
        if len(data_tmp) <= 100:
            print("Skip: " + date)
            continue
        AsOfDates.append(date)
        # process table
        data_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(data_tmp)
            
    #    analyze_intraday_data(data_tmp,"ALL_US_Transactions")
    #    analyze_intraday_data(data_tmp,file_suffix="ALL_US_Transactions",key="STT-Total",limit_red_nofed=limit_red_nofed)
    #    analyze_intraday_data(data_tmp,"ALL_US_Transactions","STT-Total",limit_red_nofed)
    
        fmus = data_tmp["FMU"].drop_duplicates().tolist()
    #    fmus = fmus[~fmus.isin([''])].tolist()
    #    legal_entity = data_tmp["CLEARING_MATERIAL_ENTITY"].drop_duplicates().tolist()
    
    #    'FED ACH' all happen in 8:30am
        for fmu in fmus:
    #        fmu = fmus[0]
            analyze_intraday_data(data_tmp[data_tmp["FMU"]==fmu],fmu.replace(" ", ""),key=fmu)
      
    #    for le in legal_entity:
    #        analyze_intraday_data(data_tmp[data_tmp["CLEARING_MATERIAL_ENTITY"]==le],le.replace(" ", ""),key=le)
            
        start_date = datetime.datetime.strptime(date+' 00:00:00', '%Y%m%d %H:%M:%S')
        end_date = datetime.datetime.strptime(date+' 23:59:59', '%Y%m%d %H:%M:%S')
        
        running_tmp = Running.loc[(Running.index>=start_date)&(Running.index<=end_date),:]
    
    #    plt.figure()
    #    figure = running_tmp.plot(style=styles,linewidth=1.3)
    #    figure.yaxis.set_major_formatter(formatter_billionsinteger)
    #    figure.xaxis.label.set_visible(False)
    #    plt.title("Running Total Balance in USD Billions",fontsize=20)
    #    plt.legend(loc='best',prop={'size':10})
    #    fig = figure.get_figure()
    #    fig.set_size_inches(10, 8)
    #    fig.savefig(plot_folder+"/IntradayLiquidity_Running_Total_LE_"+date+".png",bbox_inches='tight')
    
        plt.figure()
        figure = running_tmp[['STT-Total']+fmus].plot(style=styles,linewidth=1.3)
        figure.yaxis.set_major_formatter(formatter_billionsinteger)
        figure.xaxis.label.set_visible(False)
        plt.title("Running Total Balance in USD Billions",fontsize=20)
        plt.legend(loc='best',prop={'size':10})
        fig = figure.get_figure()
        fig.set_size_inches(10, 8)
        fig.savefig(plot_folder+"/IntradayLiquidity_Running_Total_FMU_"+date+".png",bbox_inches='tight')
    
    #################### Finish analysis and start reporting ########################
    AsOfDates = [datetime.datetime.strptime(x, "%Y%m%d") for x in AsOfDates]
    today = max(AsOfDates).strftime("%Y/%m/%d")
    AsOfDates = [x.strftime("%Y%m%d") for x in sorted(AsOfDates,reverse=True)]
    ### Execute PDF report
    file = open(pdf_dir + "/GlobalParameters.tex", "w")
    command="\\newcommand\\Output{"+plot_folder+"}\n"+\
    "\\newcommand\\AsOfDate{"+today +"}\n"+\
    "\\newcommand\\AsOfDates{"+','.join(AsOfDates)+"}\n"+\
    "\\newcommand\\FMUs{EUR-Deutsche,EUR-TARGET2,EUR-Intesa,JPY-BTMU,GBP-CREST,GBP-CHAPS,CAD-LVTS,Excluded}\n"+\
    "\\newcommand\\RunningTotalHistory{a,b}\n"
    file.write(command)
    file.close()
    
    os.chdir(pdf_dir)
    file_name = 'INTL Intradaly Liquidity Risk Monitoring Reporting-'+today.replace('/','') 
    pdf_name = file_name+".pdf"
    #j = 1
    #while os.path.exists(pdf_name):
    #    file_name2 = file_name+"-Update"+str(j)
    #    pdf_name = file_name2+".pdf"
    #    j = j + 1
    
    subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', pdf_name, './document_workingcopy.tex'])
    subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', pdf_name, './document_workingcopy.tex'])
    subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', pdf_name, './document_workingcopy.tex'])
