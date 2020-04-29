# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 16:01:25 2017
Analyze treasury common deposits file
@author: e620927
"""
SYSTEM_INITIATION = False
PRODUCTION_ENVRIONMENT = True
TEST_ENVIRONMENT = True

import datetime
################# Global Parameters  #################
if PRODUCTION_ENVRIONMENT:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes-Production"
    output_dir = "Z:/Charles/IntradayLiquidity/Output_Common"
    pdf_dir = "Z:/Charles/IntradayLiquidity/PDFReport_Common"
    TEST_ENVIRONMENT = False
    Run_regression_data = False
else:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"
    output_dir = "Z:/Charles/IntradayLiquidity/Output_Test"
    pdf_dir = "Z:/Charles/IntradayLiquidity/PDFReport_Test"

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
import statsmodels.formula.api as smf
from pandas.tseries.offsets import BMonthEnd
################# Local Libraries #################
os.chdir(code_dir)
# Load local functions
import UpdateDatabase_Intraday_DB
imp.reload(UpdateDatabase_Intraday_DB)
from UpdateDatabase_Intraday_DB import read_db, update_daily_tables

import process_IntradayLiquidity
imp.reload(process_IntradayLiquidity)
from process_IntradayLiquidity import update_table1, update_table3, update_table4, update_table_fed_balance

import Functions_Analysis
imp.reload(Functions_Analysis)
from Functions_Analysis import process_bcbs_extract_a1_report, create_unique_dirname

last_update = max(read_db("Fed_Balance").columns)

### update database to reflect the recent downloads from FTDR
update_daily_tables()
update_table_fed_balance()

if SYSTEM_INITIATION:
    update_table1()
#    update_table2()
    update_table3()
    update_table4() #update weekly or monthly
elif TEST_ENVIRONMENT:
    print("Test Environment")
#    update_table1(table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3")
#    update_table3(table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3")
#    update_table4()     # update percentiles using updated history
                        # follow monthly-update schedule, time consuming
elif PRODUCTION_ENVRIONMENT:
    update_table1(table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3") #update daily, 60 seconds
    update_table3(table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3") #update daily, 5 minutes???

if False: #All one time updates!
#    ###############if need to clean up table for historical periods ##################Be careful
#    from process_IntradayLiquidity import Cleanup_tables
#    cleanup_start = datetime.datetime.strptime("2018-07-02",'%Y-%m-%d')
#    cleanup_end = datetime.datetime.today()
#    Cleanup_tables(cleanup_start,cleanup_end)
    
    ###update Domestic A1 tables
    # 2017 data, one time only
    from UpdateDatabase_Intraday_DB import UPDATE_BCBS_248_Data_Extract_A1_Report
    UPDATE_BCBS_248_Data_Extract_A1_Report()
    # 2016 data, one time only
    from UpdateDatabase_Intraday_DB import UPDATE_RDA_BCBS_248_Data_Extract_A1_Report_2016
    UPDATE_RDA_BCBS_248_Data_Extract_A1_Report_2016()

    ###update International tables
    from UpdateDatabase_Intraday_DB import UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST
    UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST()

    ###update Step3 table from Fed balance report in FTDR
    from UpdateDatabase_Intraday_DB import UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201805","201804"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201803","201802"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201801","201712"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201711","201710"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201709","201708"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201706","201705"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201704","201703"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201702","201701"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201707"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201605","201604"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201603","201602"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201601","201612"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201611","201610"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201609","201608"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201606","201607"])
    UPDATE_DM_RTIM_DOM_ALL_TRANSACTION_STEP3_MULTI_DAY(["201607"])

##Setup parameters
if TEST_ENVIRONMENT:
    start_date = datetime.datetime.strptime('2018-09-18 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
    end_date = datetime.datetime.strptime('2018-09-18 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
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
    timewindows = [[(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d")] for x in range((end_date-start_date).days+1)]
elif PRODUCTION_ENVRIONMENT:
    start_date = last_update
    all_dates = read_db("Fed_Balance").columns
    timewindows = [[x] for x in all_dates[all_dates > start_date]]
    if len(timewindows) == 0:
        timewindows = [[max(read_db("Fed_Balance").columns)]]
    
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

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)

#new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME"
column_name_transaction_amount = "TRANSACTION_AMOUNT"
column_name_transaction_type = "TRANSACTION_TYPE"
column_name_legal_entity = "CLEARING_MATERIAL_ENTITY"
column_name_datamart = "SOURCEDATAMART"
column_name_fmu_original = "FED_CHIPS_BT"
column_name_fmu = "FMU"
column_name_running_total = "RUNNING_TOTAL"
column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"
column_name_15minutes = "Time15Minute"
column_name_30minutes = "Time30Minute"
column_name_60minutes = "Time60Minute"

#column_name_net_transaction = "NET_TOTAL_AT_TRANSCATION_TIME"

#LNNCP threshold
limit_yellow_withfed = 5E9
limit_red_withfed = 3E9
limit_red_nofed = -11.9E9

#################### Finish Configuration ####################

for timewindow in timewindows:
    #################### Start Analysis ####################
#    timewindow = timewindows[0]
    # create folder hierarchy
    
    Fed_balance = read_db("Fed_Balance").transpose()
    if not timewindow[0] in Fed_balance.index:
        continue
    
    day = datetime.date.today().strftime("%Y%m%d")
    plot_folder = output_dir+"/Output_"+day
    plot_folder = create_unique_dirname(plot_folder)
    
    if not os.path.exists(plot_folder):
        os.mkdir(plot_folder)
        
    start_time = time.time()
    
    #################### Process Horizontal Data #########
    ###Gross Payment by Credit/Debit
    balance_type = column_name_transaction_amount
    
    #STT Corp
    attribute_groupby = [column_name_transaction_type]
    table_name = balance_type+"_By_"+ "_and_".join(attribute_groupby)
    
    summary_data = read_db(table_name)
    if len(summary_data) == 0:
        exit("No file found for " + table_name)
    
    summary_data = summary_data.transpose()
    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    
    data_plot = summary_data
    data_plot = data_plot[["CREDIT","DEBIT"]]
    data_plot['Net'] = data_plot['CREDIT'] + data_plot['DEBIT'] 
    
    data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
#    plt.figure()
#    figure = data_plot.plot(style=styles,linewidth=1.3)
#    figure.yaxis.set_major_formatter(formatter_billionsinteger)
#    figure.xaxis.label.set_visible(False)
#    plt.title("Daily Credit/Debit Payments for STT Corp in USD Billions\n(Average in Parentheses)",fontsize=20)
#    plt.legend(loc="best",prop={'size':10})
#    #        plt.rcParams.update({'font.size': 12})
#    fig = figure.get_figure()
#    fig.set_size_inches(10, 8)
#    fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_STT_Corp.png",bbox_inches='tight')
    def plot_type1(tmp,title=None):
#            tmp = data_plot
        from cycler import cycler
        plt.style.use('default')
        plt.rc('lines', linewidth=2)
        custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
        
        fig, ax = plt.subplots()
        if title is not None:
            tmp.dropna().plot(ax=ax,title=title)
        else:
            tmp.dropna().plot(ax=ax)
        ax.yaxis.set_major_formatter(formatter_billions)
#        ax.tick_params(labelsize=15)
        ax.xaxis.label.set_visible(False)
        ax.set_prop_cycle(custom_cycler)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        plt.legend(loc="best",prop={'size':10})
        plt.title(title,fontsize=20)
        plt.axhline(y=0, linewidth=1, color='#969696',linestyle='--')
        fig.set_size_inches(10,8)
        return(fig)

    fig = plot_type1(data_plot,title = "Daily Credit/Debit Payments for STT Corp in USD Billions\n(Average in Parentheses)")
    fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_STT_Corp.png",bbox_inches='tight')
    
    #By LE and FMUs
    attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_fmu]
    for attribute in attributes:
    #    attribute = column_name_legal_entity
        #attribute = column_name_hour
        #attribute = column_name_fmu
    #    attribute_groupby = [column_name_transaction_type]
        attribute_groupby = [column_name_transaction_type, attribute]
    #    attribute_groupby = [column_name_transaction_type, attribute]
        
        table_name = balance_type+"_By_"+ "_and_".join(attribute_groupby)
        
        summary_data = read_db(table_name)
        if len(summary_data) == 0:
            continue
        
        summary_data = summary_data.transpose()
        summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
        
        sub_categorys = summary_data.columns.get_level_values(attribute).drop_duplicates().tolist()
    
        for sub_category in sub_categorys:
    #        sub_category = 'SSBT BOSTON'
    #        sub_category = 'SSBT NEW YORK'
            
            data_plot = summary_data[sub_category]
            if not any(data_plot.columns=="CREDIT")&any(data_plot.columns=="DEBIT"):
                continue
            data_plot = data_plot[["CREDIT","DEBIT"]]
            data_plot['Net'] = data_plot.apply(np.nansum,axis=1)
    
            data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
            
            fig = plot_type1(data_plot.fillna(0),title = "Daily Credit/Debit Payments for "+sub_category+" in USD Billions\n(Average in Parentheses)")
            fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
            
#            plt.figure()
#            figure = data_plot.plot(style=styles,linewidth=1.3)
#            figure.yaxis.set_major_formatter(formatter_billionsinteger)
#            figure.xaxis.label.set_visible(False)
#            plt.title("Daily Credit/Debit Payments for "+sub_category+" in USD Billions\n(Average in Parentheses)",fontsize=20)
#            plt.legend(loc='best',prop={'size':10})
#    #        plt.rcParams.update({'font.size': 12})
#            fig = figure.get_figure()
#            fig.set_size_inches(10, 8)
#            fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
        
    ## Analyze running total
    Running = read_db("RUNNINGTOTAL_TRANSACTION_AMOUNT")
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
    
    def plot_lnncp(tmp,p50,p75,p95,p99,title=None):
#            tmp = result_tmp[[stat_type]]
        tmp.columns = [tmp.columns[0] + "("+ str(billions(p50)) + "/" + str(billions(p75)) + "/" + str(billions(p95))+ "/" + str(billions(p99))+")"]
        
        from cycler import cycler
        plt.style.use('default')
        plt.rc('lines', linewidth=1)
        custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
        
        fig, ax = plt.subplots()
        if title is not None:
            tmp.dropna().plot(ax=ax,title=title)
        else:
            tmp.dropna().plot(ax=ax)
        ax.yaxis.set_major_formatter(formatter_billions)
#        ax.tick_params(labelsize=15)
        ax.xaxis.label.set_visible(False)
        ax.set_prop_cycle(custom_cycler)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        ax.axhline(y=p50,linewidth=2,zorder=0,color='#14beff')
        ax.axhline(y=p75,linewidth=2,zorder=0,color='#fccc00')
        ax.axhline(y=p95,linewidth=2,zorder=0,color='#e28100')
        ax.axhline(y=p99,linewidth=2,zorder=0,color='#8c00af')

        plt.legend(loc="best",prop={'size':10})
        plt.title(title,fontsize=20)
        plt.axhline(y=0, linewidth=1, color='#969696',linestyle='--')
        fig.set_size_inches(10,8)
        return(fig)

    def plot_lnncp_time(tmp,title):
#                tmp = result_tmp
        lnncp_time = [x.time() for x in tmp['LNNCP_Time']]
        lpncp_time = [x.time() for x in tmp['LPNCP_Time']]
        
        from cycler import cycler
        plt.style.use('default')
        plt.rc('lines', linewidth=0.5)
        custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
        fig, ax = plt.subplots()
        ax.plot_date(tmp.index,lnncp_time)
        ax.plot_date(tmp.index,lpncp_time)
        ax.legend(["LNNCP Timing","LPNCP Timing"],loc="best")
        ax.xaxis.label.set_visible(False)
        ax.set_prop_cycle(custom_cycler)
        ax.set_title(title,fontsize=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19,23]]
        ax.set_yticks(custom_tick_locs)
#        plt.legend(loc="best",prop={'size':10})
        fig.set_size_inches(12,9)
        return(fig)
    
    custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
    
    sub_categories = Running.columns
    for sub_category in sub_categories:
    #    sub_category = 'Fedwire Securities'
        result_tmp = Running[sub_category].resample('1D').apply([extract_lnncp,extract_lnncp_time,extract_lpncp,extract_lpncp_time])
        result_tmp.columns = ['LNNCP','LNNCP_Time','LPNCP','LPNCP_Time']
        result_tmp = result_tmp.dropna()
        result_tmp.to_excel(plot_folder+"/LNNCP_LPNCP_Value_and_Timing_"+sub_category.replace(" ","")+".xlsx")
        
        stat_type = 'LPNCP'
        result_tmp[[stat_type]] = result_tmp[[stat_type]].astype(float)
        p50 = np.nanpercentile(result_tmp[[stat_type]],50)
        p75 = np.nanpercentile(result_tmp[[stat_type]],75)
        p95 = np.nanpercentile(result_tmp[[stat_type]],95)
        p99 = np.nanpercentile(result_tmp[[stat_type]],99)
    
        fig = plot_lnncp(result_tmp[[stat_type]],p50,p75,p95,p99,title="Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 75th, 95th and 99th Percentiles")
        fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
        plt.clf()
        
        stat_type = 'LNNCP'
        result_tmp[[stat_type]] = result_tmp[[stat_type]].astype(float)
        p50 = np.nanpercentile(result_tmp[[stat_type]],50)
        p25 = np.nanpercentile(result_tmp[[stat_type]],25)
        p5 = np.nanpercentile(result_tmp[[stat_type]],5)
        p1 = np.nanpercentile(result_tmp[[stat_type]],1)

        fig = plot_lnncp(result_tmp[[stat_type]],p50,p25,p5,p1,title="Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 25th, 5th and 1st Percentiles")
        fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
        plt.clf()

        fig = plot_lnncp_time(result_tmp,title="Timing of LNNCP and LPNCP for " + sub_category)
        fig.savefig(plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_Timing.png",bbox_inches='tight')
        plt.clf()
        
#        # for summary page
#        Fed_balance = read_db("Fed_Balance").transpose()
#        if sub_category in ['SSBT BOSTON']:
##            sub_category = "SSBT BOSTON"
#            stat_type = 'LPNCP'
#            result_tmp[[stat_type]] = result_tmp[[stat_type]].astype(float)
#            result_tmp.tail(22)[stat_type].plot()
#            p50 = np.nanpercentile(result_tmp[[stat_type]],50)
#            p75 = np.nanpercentile(result_tmp[[stat_type]],75)
#            p95 = np.nanpercentile(result_tmp[[stat_type]],95)
#            p99 = np.nanpercentile(result_tmp[[stat_type]],99)
#        fig, ax = plt.subplots()
#        result_tmp[[stat_type]].dropna().plot(ax=ax,style=styles)
#        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#        ax.axhline(y=p50,linewidth=2,zorder=0,color='y')
#        ax.axhline(y=p75,linewidth=2,zorder=0,color='m')
#        ax.axhline(y=p95,linewidth=2,zorder=0,color='g')
#        ax.yaxis.set_major_formatter(formatter_billions)
#        ax.tick_params(labelsize=20)
#        ax.xaxis.label.set_visible(False)
#        ax.set_title("Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 75th and 95th Percentiles",fontsize=20)
#        fig.set_size_inches(12,9)
#        fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
#        plt.clf()
#        lnncp_time = [x.time() for x in result_tmp[stat_type+'_Time']]
#        fig, ax = plt.subplots()
#        ax.plot_date(result_tmp.index,lnncp_time)
#        ax.xaxis.label.set_visible(False)
#        ax.set_title("Timing of "+stat_type + " for " + sub_category,fontsize=20)
#        plt.yticks(custom_tick_locs)
#        fig.set_size_inches(12,9)
#        fig.savefig(plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_"+stat_type+"_Timing.png",bbox_inches='tight')
#        plt.clf()
#        
#        stat_type = 'LNNCP'
#        p50 = np.nanpercentile(result_tmp[[stat_type]],50)
#        p25 = np.nanpercentile(result_tmp[[stat_type]],25)
#        p5 = np.nanpercentile(result_tmp[[stat_type]],5)
#    
#        fig, ax = plt.subplots()
#        result_tmp[[stat_type]].dropna().plot(ax=ax,style=styles)
#        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#        ax.axhline(y=p50,linewidth=2,zorder=0,color='y')
#        ax.axhline(y=p25,linewidth=2,zorder=0,color='m')
#        ax.axhline(y=p5,linewidth=2,zorder=0,color='g')
#        ax.yaxis.set_major_formatter(formatter_billions)
#        ax.tick_params(labelsize=20)
#        ax.xaxis.label.set_visible(False)
#        ax.set_title("Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 25th and 5th Percentiles",fontsize=20)
#        fig.set_size_inches(12,9)
#        fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
#        plt.clf()
#            
#        lnncp_time = [x.time() for x in result_tmp[stat_type+'_Time']]
#        fig, ax = plt.subplots()
#        ax.plot_date(result_tmp.index,lnncp_time)
#        ax.xaxis.label.set_visible(False)
#        ax.set_title("Timing of "+stat_type + " for " + sub_category,fontsize=20)
#        plt.yticks(custom_tick_locs)
#        fig.set_size_inches(12,9)
#        fig.savefig(plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_"+stat_type+"_Timing.png",bbox_inches='tight')
#        plt.clf()
#        
#        filename = plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_LNNCP_LPNCP_Timing.xlsx"
#        result_tmp.to_excel(filename)
        
    #Net Transactional Amount of time bucket
    for attribute_groupby in [column_name_hourminue, column_name_15minutes,column_name_30minutes,column_name_60minutes]:
#        attribute_groupby = column_name_60minutes
        file_name = balance_type+"_By_"+ attribute_groupby
        tmp_data = read_db(file_name)
        
        if len(tmp_data) == 0:
            continue
        tmp_data.index = [datetime.datetime.strptime(x,"%H:%M").time() for x in tmp_data.index]
        tmp_data_df = tmp_data.fillna(method='ffill').fillna(0)
    #    running_time_df.plot()
        percentiles = pd.DataFrame({"1th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,1),axis=1),\
                                    "5th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,5),axis=1),\
                                    "25th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,25),axis=1),\
                                    "50th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,50),axis=1),\
                                    "75th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,75),axis=1),\
                                    "95th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,95),axis=1),\
                                    "99th Percentile":tmp_data_df.apply(lambda x: np.nanpercentile(x,99),axis=1)})
        percentiles = percentiles[["1th Percentile","5th Percentile","25th Percentile","50th Percentile","75th Percentile","95th Percentile","99th Percentile"]]
    
        for date in timewindow:
    #        date = timewindow[0]
            if date in tmp_data.columns:
                fig, ax = plt.subplots()
                tmp_data[date].dropna().plot(ax=ax,color="black",linewidth=2)
                percentiles.dropna().plot(ax=ax,style=styles2,alpha=0.5)
                trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
                ax.yaxis.set_major_formatter(formatter_billions)
                ax.tick_params(labelsize=15)
                plt.xticks(custom_tick_locs,rotation=90)
                ax.xaxis.label.set_visible(False)
                ax.set_title("Net Transaction Amount by " + attribute_groupby + " for " + date,fontsize=20)
                fig.set_size_inches(12,9)
                fig.savefig(plot_folder+"/IntradayLiquidity_net_amount_by_"+ attribute_groupby +"_for_"+date+".png",bbox_inches='tight')
                plt.clf()
    
        ## Running balance and Transactional Amount
        #start of periods
        Run_regression_data = False
        if Run_regression_data:
#            start_of_period = Running['STT-Total'].resample(attribute_groupby[4:6]+'T').first()
            
            start_of_period = tmp_data.apply(np.cumsum).shift(1)
            start_of_period.iloc[0,:] = 0
            
            start_of_period_stacked = start_of_period.transpose().stack()
            a = start_of_period_stacked.index.get_level_values(0)
            b = start_of_period_stacked.index.get_level_values(1)
            time_stamp = [x +" " + str(y) for x,y in zip(a,b)]
            start_of_period_stacked.index = [datetime.datetime.strptime(x,"%Y%m%d %H:%M:%S") for x in time_stamp]
            start_of_period_stacked.name = "StartingRunningBalance"
            
            tmp_data_stacked = tmp_data.stack()
            a = tmp_data_stacked.index.get_level_values(0)
            b = tmp_data_stacked.index.get_level_values(1)
            time_stamp = [y +" " + str(x) for x,y in zip(a,b)]
            tmp_data_stacked.index = [datetime.datetime.strptime(x,"%Y%m%d %H:%M:%S") for x in time_stamp]
            tmp_data_stacked.name = "NetTransactionalAmount"
            
            relational_data = start_of_period_stacked.to_frame("StartingBalance").join(tmp_data_stacked).dropna()
            relational_data = relational_data.sort_index()
            
            relational_data['TimeInterval'] = relational_data.index
            
            dates_BD1 = relational_data['TimeInterval'].resample('M').first()
            quarterly_dates = relational_data['TimeInterval'].resample('1Q').last()
            montly_dates = relational_data['TimeInterval'].resample('1M').last()
            dates_BD1 = [x.date() for x in dates_BD1]
            quarterly_dates = [x.date() for x in quarterly_dates]
            montly_dates = [x.date() for x in montly_dates]
            montly_dates = [x for x in montly_dates if x not in quarterly_dates]
            all_dates = [x.date() for x in relational_data.index]
            
            def determine_date(tmp_date):
        #        tmp_date = all_dates[0]    
                if tmp_date in dates_BD1:
                    return("BD1")
                elif tmp_date in quarterly_dates:
                    return("QE")
                elif tmp_date in montly_dates:
                    return("ME")
                else:
                    return("BAU")
    
            relational_data['DateType'] = [determine_date(x) for x in all_dates]
            relational_data['TimeInterval'] = [str(x.time()) for x in relational_data['TimeInterval']]
            if attribute_groupby !=column_name_hourminue:
                filename = plot_folder+"/Regression_Data"+ attribute_groupby +".xlsx"
                relational_data.to_excel(filename)
            
            lm = smf.ols('NetTransactionalAmount ~ StartingBalance', data = relational_data).fit()
#            lm.summary()
#            relational_data.head()
            fig, ax = plt.subplots()
            plt.scatter(relational_data['StartingBalance'], relational_data['NetTransactionalAmount'], c = "b",s=0.5)
            plt.scatter(relational_data['StartingBalance'], lm.predict(), c = "red",s=1)
            plt.xlabel('StartingBalance')
            plt.ylabel('NetTransactionalAmount')
            plt.title("Regression Result for "+attribute_groupby+"\nNetTransactionalAmount ~ StartingBalance; R-squared: " + percentages(lm.rsquared))
            ax.yaxis.set_major_formatter(formatter_billions)
            ax.xaxis.set_major_formatter(formatter_billions)
            fig.set_size_inches(12,9)
            fig.savefig(plot_folder+"/Regression_Result"+ attribute_groupby +".jpg")
            text_file = open(plot_folder+"/Regression_Result"+ attribute_groupby +".txt", "w")
            text_file.write(str(lm.summary()))
            text_file.close()
            
            lm = smf.ols('NetTransactionalAmount ~ StartingBalance + TimeInterval', data = relational_data).fit()
#            lm.summary()
#            relational_data.head()
            
            categories = np.unique( relational_data['TimeInterval'])
            colors = np.linspace(0, 5, len(categories))
            colordict = dict(zip(categories, colors))  
            relational_data["Color"] = relational_data['TimeInterval'].apply(lambda x: colordict[x])
            fig, ax = plt.subplots()
            plt.scatter(relational_data['StartingBalance'], relational_data['NetTransactionalAmount'], c = relational_data['Color'],s=0.5)
            plt.scatter(relational_data['StartingBalance'], lm.predict(), c = "red",s=0.5)
            plt.xlabel('StartingBalance')
            plt.ylabel('NetTransactionalAmount')
            plt.title("Regression Result for "+attribute_groupby+"\nNetTransactionalAmount ~ StartingBalance + " + attribute_groupby+"; R-squared: " + percentages(lm.rsquared))
            ax.yaxis.set_major_formatter(formatter_billions)
            ax.xaxis.set_major_formatter(formatter_billions)
            fig.set_size_inches(12,9)
            fig.savefig(plot_folder+"/Regression_Result"+ attribute_groupby +"2.jpg")
            text_file = open(plot_folder+"/Regression_Result"+ attribute_groupby +"2.txt", "w")
            text_file.write(str(lm.summary()))
            text_file.close()
            
        
    #################### Analyze specific day's data #########
    #plot with and without beginning balance
    def plot2(tmp,title=None,flag=False,yformatter = formatter_billions):
#            tmp = running_tmp[['STT-Total']+legal_entity].dropna()
        from cycler import cycler
        plt.style.use('default')
        plt.rc('lines', linewidth=3)
        custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
        

        fig, ax = plt.subplots()
        if title is not None:
            tmp.dropna().plot(ax=ax,title=title)
        else:
            tmp.dropna().plot(ax=ax)
        ax.title.set_size(20)
        ax.yaxis.set_major_formatter(yformatter)
        ax.tick_params(labelsize=15)
#            ax.xaxis.set_major_formatter(myFmt)
        custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
        plt.xticks(custom_tick_locs,rotation=90)

        ax.xaxis.label.set_visible(False)
        ax.set_prop_cycle(custom_cycler)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        if flag == True:
            lnncp = min(tmp)
            lpncp = max(tmp)
            lnncp_time = tmp[tmp == lnncp].index[0]
            lpncp_time = tmp[tmp == lpncp].index[0]
            ax.axhline(y=lnncp,linewidth=2,zorder=0,color='mediumvioletred')
            ax.text(0.85, 0.9,"Maximum: " + str(round(lpncp/1e9,1))  + "/Time: "+ lpncp_time.strftime("%H:%M"),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
            ax.text(0.85, 0.1,"Minimum: " + str(round(lnncp/1e9,1)) + "/Time: "+ lnncp_time.strftime("%H:%M") ,horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)

        plt.axhline(y=0, linewidth=1, color='#969696',linestyle='--')

        fig.set_size_inches(12,9)
        return(fig)

    def analyze_intraday_data(tmp_data,file_suffix,key,limit_red_nofed = None, fed_balance = None):
    #        tmp_data=data_tmp[data_tmp[column_name_legal_entity]==le]
    #          file_suffix = fmu.replace(" ", "")
    #        tmp_data = data_tmp[data_tmp["CLEARING_MATERIAL_ENTITY"]==le]
    #        tmp_data = data_tmp.copy()
    #    file_suffix = "ALL_US_Transactions"
        #key = fmu
    #    fed_balance = Fed_balance.loc[date,'Fed_Balance']
        if len(tmp_data) == 0:
            return()
        
        ###transaction-level analysis
        # largest 10-25 transactons, when who
        top_number = 25
        threshold = tmp_data[column_name_transaction_amount].sort_values(ascending=False)[top_number]
        
        if column_name_running_total in tmp_data.columns:
            result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] > threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,column_name_running_total,column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
        else:
            result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] > threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,'CALC_RUNNING_TOTAL',column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
            
        result_largest_transaction.sort_values(by=[column_name_transaction_amount],ascending=False,inplace=True)
        result_largest_transaction.sort_values(by=[column_name_hour],ascending=True,inplace=True)
        result_largest_transaction.columns = ['Time', 'TimeBucket', 'Amount', 'RunningTot','Type','FMU','FedAccount']
        result_largest_transaction[['Amount','RunningTot']] = result_largest_transaction[['Amount','RunningTot']].applymap(billions)
        result_largest_transaction.index = range(1,result_largest_transaction.shape[0]+1)
        file_name = plot_folder+"/IntradayLiquidity_largest_credit_transactions_"+date+"_"+file_suffix+".tex"
        result_largest_transaction.to_latex(file_name,longtable=True)
        
        threshold = tmp_data[column_name_transaction_amount].sort_values(ascending=True)[top_number]
        if column_name_running_total in tmp_data.columns:
            result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] < threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,column_name_running_total,column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
        else:
            result_largest_transaction = tmp_data.loc[tmp_data[column_name_transaction_amount] < threshold,[column_name_transaction_time,column_name_hour,column_name_transaction_amount,'CALC_RUNNING_TOTAL',column_name_transaction_type,column_name_fmu,column_name_legal_entity]]
            
        result_largest_transaction.sort_values(by=[column_name_transaction_amount],ascending=True,inplace=True)
        result_largest_transaction.sort_values(by=[column_name_hour],ascending=True,inplace=True)
    
        result_largest_transaction.columns = ['Time', 'TimeBucket', 'Amount', 'RunningTot','Type','FMU','FedAccount']
        result_largest_transaction[['Amount','RunningTot']] = result_largest_transaction[['Amount','RunningTot']].applymap(billions)
        result_largest_transaction.index = range(1,result_largest_transaction.shape[0]+1)
        file_name = plot_folder+"/IntradayLiquidity_largest_debit_transactions_"+date+"_"+file_suffix+".tex"
        result_largest_transaction.to_latex(file_name,longtable=True)
        
        ###Running total analysis
        data_tmp_nobalance = tmp_data.groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
        data_tmp_nobalance[column_name_running_total] = data_tmp_nobalance[column_name_transaction_amount].cumsum()
    
        fig = plot2(data_tmp_nobalance[column_name_running_total].dropna(),flag=True,title="Net Cumulative Balance "+date+": " + file_suffix)
        fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()

#        lnncp = min(data_tmp_nobalance[column_name_running_total])
#        lpncp = max(data_tmp_nobalance[column_name_running_total])
#        
#        lnncp_time = data_tmp_nobalance[data_tmp_nobalance[column_name_running_total] == lnncp].index[0]
#        lpncp_time = data_tmp_nobalance[data_tmp_nobalance[column_name_running_total] == lpncp].index[0]
#        
#        fig, ax = plt.subplots()
#        data_tmp_nobalance[column_name_running_total].dropna().plot(ax=ax,style=styles)
#        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#        if limit_red_nofed is not None:
#            ax.fill_between(data_tmp_nobalance[column_name_running_total].index, 0, 1, where=data_tmp_nobalance[column_name_running_total] < limit_red_nofed, facecolor='red', alpha=0.5, transform=trans)
#            ax.axhline(y=limit_red_nofed,linewidth=2,zorder=0,color='red')
#            ax.text(0.1, 0.1,'Red Limit: '+str(formatter_billions(limit_red_nofed)),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
#        ax.axhline(y=lnncp,linewidth=2,zorder=0,color='mediumvioletred')
#        ax.text(0.85, 0.9,"LPNCP: " + str(round(lpncp/1e9,1))  + "/Time: "+ lpncp_time.strftime("%H:%M"),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
#        ax.text(0.85, 0.1,"LNNCP: " + str(round(lnncp/1e9,1)) + "/Time: "+ lnncp_time.strftime("%H:%M") ,horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
#        ax.yaxis.set_major_formatter(formatter_billions)
#        ax.tick_params(labelsize=15)
#        custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
#        plt.xticks(custom_tick_locs,rotation=90)
#        ax.xaxis.label.set_visible(False)
#        ax.set_title("Running Total Balance "+date+": " + file_suffix,fontsize=20)
#        fig.set_size_inches(12,9)
#        fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+".png",bbox_inches='tight')
#        plt.clf()
        
        if fed_balance is not None:
            fig = plot2(data_tmp_nobalance[column_name_running_total].add(fed_balance).dropna(),flag=True,title="Running Total Balance "+date+": " + file_suffix)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+".png",bbox_inches='tight')
            plt.clf()
        
        ## calculate daily statistics and output to latex
        def daily_statistics(net_cumulative, starting_balance=None):
#            net_cumulative = data_tmp_nobalance[column_name_running_total]
#            starting_balance = fed_balance
#            net_cumulative.plot()
            
            offset = BMonthEnd()
            date_time = datetime.datetime.strptime(date,"%Y%m%d")
            month_end_date = offset.rollforward(datetime.date(date_time.year,date_time.month,date_time.day))
            
            if month_end_date == date_time:
                end_of_month = "Yes"
            else:
                end_of_month = "No"
            
            lnncp = min(net_cumulative)
            lnncp_time = net_cumulative[net_cumulative == lnncp].index[0]
#            lpncp = max(net_cumulative)
#            lpncp_time = net_cumulative[net_cumulative == lpncp].index[0]
            
            if starting_balance is not None:
                Start_balance = starting_balance
                ending_balance = net_cumulative[-1] + Start_balance
                minimum_balance = lnncp + starting_balance
                result = pd.DataFrame({"":[date,formatter_billions(Start_balance),formatter_billions(ending_balance),formatter_billions(minimum_balance),lnncp_time,end_of_month,formatter_billions(lnncp)]})
                result.index = ["Date","Starting Balance","Ending Balance","Minimum Balance","Time","End-of-Month","LNNCP"]
                return(result)
            else:
                result = pd.DataFrame({"":[date,formatter_billions(lnncp),lnncp_time,end_of_month]})
                result.index = ["Date","LNNCP","Time","End-of-Month"]
                return(result)
        
        file_name = plot_folder+"/IntradayLiquidity_statistics_"+date+"_"+file_suffix+".tex"
        stats = daily_statistics(data_tmp_nobalance[column_name_running_total], fed_balance)
        stats.to_latex(file_name,longtable=True)
        
        ## with corridor
        table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_"+key
        percentiles_runningtotal = read_db(table_name)
#        red_corridor = '1th Percentile'
#        yellow_corridor = '5th Percentile'
        
        def plot3(tmp,red_corridor="1th Percentile",title=None):
#            tmp = data_tmp_nobalance_with_corridor
            from cycler import cycler
            plt.style.use('default')
            plt.rc('lines', linewidth=1)
            custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
            
            fig, ax = plt.subplots()
            if title is not None:
                tmp[column_name_running_total].dropna().plot(ax=ax,title=title,color="black",linewidth=2)
            else:
                tmp.dropna().plot(ax=ax)
            tmp.iloc[:,1:].dropna().plot(ax=ax,style=styles2,alpha=0.5)
#            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#            ax.fill_between(tmp[column_name_running_total].index, 0, 1, where=tmp[column_name_running_total] < tmp[red_corridor], facecolor='red', alpha=0.2, transform=trans)

            ax.yaxis.set_major_formatter(formatter_billions)
            ax.tick_params(labelsize=15)
#            ax.xaxis.set_major_formatter(myFmt)
            custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
            plt.xticks(custom_tick_locs,rotation=90)

            ax.xaxis.label.set_visible(False)
            ax.set_prop_cycle(custom_cycler)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            plt.axhline(y=0, linewidth=1, color='#969696',linestyle='--')
            fig.set_size_inches(12,9)
            return(fig)
            
        if len(percentiles_runningtotal) >0:
            percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
            data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].join(percentiles_runningtotal)
            fig = plot3(data_tmp_nobalance_with_corridor,title ="Net Cumulative Balance "+date+" with Percentiles: " + file_suffix)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
            data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_net_cumulative_balance_"+date+"_"+file_suffix+"_with_corridor.xlsx")

#        if len(percentiles_runningtotal) >0:
#            data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].join(percentiles_runningtotal)
#            fig, ax = plt.subplots()
#            data_tmp_nobalance_with_corridor[column_name_running_total].dropna().plot(ax=ax,color="black",linewidth=2)
#            percentiles_runningtotal.dropna().plot(ax=ax,style=styles2,alpha=0.5)
#            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#            ax.fill_between(data_tmp_nobalance_with_corridor[column_name_running_total].index, 0, 1, where=data_tmp_nobalance_with_corridor[column_name_running_total] < data_tmp_nobalance_with_corridor[red_corridor], facecolor='red', alpha=0.5, transform=trans)
#            ax.tick_params(labelsize=15)
#            plt.xticks(custom_tick_locs,rotation=90)
#            ax.xaxis.label.set_visible(False)
#            ax.set_title("Running Total Balance "+date+" with Percentiles: " + file_suffix,fontsize=20)
#            ax.yaxis.set_major_formatter(formatter_billions)
#            fig.set_size_inches(12,9)
#            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
#            plt.clf()
     
        if fed_balance is not None:
            table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_with_FedBalance_"+key
            percentiles_runningtotal = read_db(table_name)

            if len(percentiles_runningtotal) >0:
                percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
                data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].add(fed_balance).join(percentiles_runningtotal)
                
                fig = plot3(data_tmp_nobalance_with_corridor,title ="Running Total Balance "+date+" with Percentiles: " + file_suffix)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
                data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_running_balance_"+date+"_"+file_suffix+"_with_corridor.xlsx")
                
#                fig, ax = plt.subplots()
##                ax.yaxis.set_major_formatter(formatter_billions)
#                data_tmp_nobalance_with_corridor[column_name_running_total].dropna().plot(ax=ax,color="black",linewidth=2)
#                percentiles_runningtotal.dropna().plot(ax=ax,style=styles2,alpha=0.5)
#                trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#                ax.fill_between(data_tmp_nobalance_with_corridor[column_name_running_total].index, 0, 1, where=data_tmp_nobalance_with_corridor[column_name_running_total] < data_tmp_nobalance_with_corridor[yellow_corridor], facecolor='orange', alpha=0.5, transform=trans)
#                ax.fill_between(data_tmp_nobalance_with_corridor[column_name_running_total].index, 0, 1, where=data_tmp_nobalance_with_corridor[column_name_running_total] < data_tmp_nobalance_with_corridor[red_corridor], facecolor='red', alpha=0.5, transform=trans)
#                ax.tick_params(labelsize=15)
#                plt.xticks(custom_tick_locs,rotation=90)
#                ax.xaxis.label.set_visible(False)
#                ax.set_title("Running Total Balance "+date+" with Percentiles: " + file_suffix,fontsize=20)
#                fig.set_size_inches(12,9)
#                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
#                plt.clf()
    
        #through put graphs
        data_tmp_credit = tmp_data[tmp_data[column_name_transaction_type] == "CREDIT"].groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
        data_tmp_debit = tmp_data[tmp_data[column_name_transaction_type] == "DEBIT"].groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
        data_tmp_credit[column_name_running_total] = data_tmp_credit[column_name_transaction_amount].cumsum()
        data_tmp_debit[column_name_running_total] = data_tmp_debit[column_name_transaction_amount].cumsum()
        
        throughput_credit = data_tmp_credit[column_name_running_total]/max(data_tmp_credit[column_name_running_total])
        throughput_debit = data_tmp_debit[column_name_running_total]/min(data_tmp_debit[column_name_running_total])
        
        #abosolute amount: combined
        thoughput_data = pd.DataFrame({"Credit Throughput":data_tmp_credit[column_name_running_total],"Debit Throughput":(-1*data_tmp_debit[column_name_running_total])})
        
        fig = plot2(thoughput_data.fillna(method='ffill'),title="Throughput Analysis "+date+": " + file_suffix,flag=False)
        fig.savefig(plot_folder+"/IntradayLiquidity_throughput_amount_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()
        
        #abosolute amount: credit
        table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_"+key
#        table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_CREDIT_15min"
        
        percentiles_runningtotal = read_db(table_name)

        if len(percentiles_runningtotal) >0:
            percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
            data_tmp_nobalance_with_corridor = data_tmp_credit[[column_name_running_total]].join(percentiles_runningtotal,how="left")
            fig = plot3(data_tmp_nobalance_with_corridor,title ="Throughput Analysis for Credit Transactions for "+file_suffix +": "+date)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_credit_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
            plt.clf()
    
        #abosolute amount: debit
        table_name = "RUNNINGTOTAL_TRANSACTION_AMOUNT_DEBIT_"+key
        
        percentiles_runningtotal = read_db(table_name)
    
        if len(percentiles_runningtotal) >0:
            percentiles_runningtotal.index = [datetime.datetime.strptime(x,'%H:%M:%S').time() for x in percentiles_runningtotal.index]
            
            data_tmp_nobalance_with_corridor = data_tmp_debit[[column_name_running_total]].join(percentiles_runningtotal,how="left")
            fig = plot3(-1*data_tmp_nobalance_with_corridor,red_corridor="99th Percentile",title ="Throughput Analysis for Debit Transactions for "+file_suffix +": "+date)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_debit_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
            plt.clf()
        #percentage term: combined
        thoughput_data = pd.DataFrame({"Credit Throughput":throughput_credit,"Debit Throughput":throughput_debit})
        fig = plot2(thoughput_data,title="Throughput Analysis "+date+": " + file_suffix,flag=False,yformatter=formatter_percentages)
        fig.savefig(plot_folder+"/IntradayLiquidity_throughput_percentage_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()

        return(stats)

    Fed_balance = read_db("Fed_Balance").transpose()
    #fed_balance.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in fed_balance.index]
    
    AsOfDates = []
    
    for date in timewindow:
    #    date = timewindow[0]
    #    date = "20180629"
        if datetime.datetime.strptime(date,"%Y%m%d") < datetime.datetime.strptime("20180701","%Y%m%d"):
            table_name = "BCBS_248_Data_Extract_A1_Report"
        else:
            table_name = "DM_RTIM_DOM_ALL_TRANSACTION_STEP3"
    
        data_tmp = read_db(table_name,date)
        if len(data_tmp) <= 100:
            print("Skip: " + date)
            continue
        AsOfDates.append(date)
        # process table
    #    if table_name == "BCBS_248_Data_Extract_A1_Report":
        data_tmp = process_bcbs_extract_a1_report(data_tmp)
        
        if date in Fed_balance.index:
            analyze_intraday_data(data_tmp,file_suffix="ALL_US_Transactions",key="STT-Total",limit_red_nofed=limit_red_nofed, fed_balance=Fed_balance.loc[date,'Fed_Balance'])
        else:
            analyze_intraday_data(data_tmp,file_suffix="ALL_US_Transactions",key="STT-Total",limit_red_nofed=limit_red_nofed)
            
        fmus = data_tmp["FMU"].drop_duplicates()
        fmus = fmus[~fmus.isin(['DTCC - FICC',"BOOK TRANSFER"])].tolist()
        legal_entity = data_tmp[column_name_legal_entity].drop_duplicates().tolist()
    
    #    'FED ACH' all happen in 8:30am
        for fmu in fmus:
            analyze_intraday_data(data_tmp[data_tmp["FMU"]==fmu],fmu.replace(" ", ""),key=fmu)
      
        stats = pd.DataFrame()
        for le in legal_entity:
#            le = legal_entity[1]
            if le == "SSBT BOSTON":
                stat = analyze_intraday_data(data_tmp[data_tmp[column_name_legal_entity]==le],file_suffix=le.replace(" ", ""),key=le,fed_balance=Fed_balance.loc[date,'Fed_Balance'])
            elif le == "SSBT NEW YORK":
                stat = analyze_intraday_data(data_tmp[data_tmp[column_name_legal_entity]==le],file_suffix=le.replace(" ", ""),key=le,fed_balance=0)
            stat.columns = [le]
            if len(stats) == 0:
                stats = stat
            else:
                stats = stats.join(stat,how="outer")
        stats[["SSBT BOSTON","SSBT NEW YORK"]].to_latex(plot_folder+"/IntradayLiquidity_Stats_LE_"+date+".tex",longtable=True)
        
        # Plot through preprocessed Running Total results
        start_date = datetime.datetime.strptime(date+' 00:00:00', '%Y%m%d %H:%M:%S')
        end_date = datetime.datetime.strptime(date+' 23:59:59', '%Y%m%d %H:%M:%S')
        
        running_tmp = Running.loc[(Running.index>=start_date)&(Running.index<=end_date),:]
        running_tmp.index = [x.time() for x in running_tmp.index]
    
        fig = plot2(running_tmp[['STT-Total']+legal_entity],title="Running Total Balance in USD Billions",flag=False)
        fig.savefig(plot_folder+"/IntradayLiquidity_Running_Total_LE_"+date+".png",bbox_inches='tight')
        plt.clf()

        fig = plot2(running_tmp[['STT-Total']+fmus],title="Running Total Balance in USD Billions",flag=False)
        fig.savefig(plot_folder+"/IntradayLiquidity_Running_Total_FMU_"+date+".png",bbox_inches='tight')
        plt.clf()
        
    AsOfDates = [datetime.datetime.strptime(x, "%Y%m%d") for x in AsOfDates]
    today = max(AsOfDates).strftime("%Y/%m/%d")
    AsOfDates = [x.strftime("%Y%m%d") for x in sorted(AsOfDates,reverse=True)]
    ### Execute PDF report
    file = open(pdf_dir + "/GlobalParameters.tex", "w")
    command="\\newcommand\\Output{"+plot_folder+"}\n"+\
    "\\newcommand\\AsOfDate{"+today +"}\n"+\
    "\\newcommand\\AsOfDates{"+','.join(AsOfDates)+"}\n"+\
    "\\newcommand\\FMUs{CHIPS,FedwireFunds,FedwireSecurities}\n"+\
    "\\newcommand\\LE{SSBTBOSTON,SSBTNEWYORK}\n"+\
    "\\newcommand\\TimeBucket{01-02,02-03,03-04,04-05,05-06,06-07,07-08,08-09,09-10,10-11,11-12,12-13,13-14,14-15,15-16,16-17,17-18,18-19,19-20}\n"+\
    "\\newcommand\\RunningTotalHistory{a,b}\n"
    file.write(command)
    file.close()
    
    os.chdir(pdf_dir)
    file_name = 'Intradaly Liquidity Risk Monitoring Reporting-'+today.replace('/','') 
    pdf_name = file_name+".pdf"
#    j = 1
#    while os.path.exists(pdf_name):
#        file_name2 = file_name+"-Update"+str(j)
#        pdf_name = file_name2+".pdf"
#        j = j + 1
    
    subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', pdf_name, './document_workingcopy.tex'])
    subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', pdf_name, './document_workingcopy.tex'])
    subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', pdf_name, './document_workingcopy.tex'])

####Netpayment
#attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_fmu,column_name_transaction_type]
#
#for attribute_groupby in attributes:
##    attribute_groupby = column_name_legal_entity
##    attribute_groupby = column_name_hour
##    attribute_groupby = column_name_fmu
##    attribute_groupby = column_name_datamart
##    attribute_groupby = column_name_transaction_type
#
#    table_name = balance_type+"_By_"+ attribute_groupby
#    
#    summary_data = read_db(table_name)
#    if len(summary_data) == 0:
#        continue
#    
#    summary_data = summary_data.transpose()
#    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
#    
#    if summary_data.shape[1] >= 8:
#        k = 1
#        for i in range(0,summary_data.shape[1],4):
#            data_plot = summary_data.iloc[:,i:(i+4)].copy()
#            data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
#            plt.figure()
#            figure = data_plot.plot(style=styles,linewidth=1.3)
#            figure.yaxis.set_major_formatter(formatter_billionsinteger)
#            figure.xaxis.label.set_visible(False)
#            plt.title("Daily Net Payment By "+attribute_groupby+" in USD Billions\n(Average in Parentheses)",fontsize=20)
#            plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
##            plt.rcParams.update({'font.size': 12})
#            fig = figure.get_figure()
#            fig.set_size_inches(10, 8)
#            fig.savefig(plot_folder+"/History_Chart_By_NetPayments_"+attribute_groupby+"_"+str(k)+".png",bbox_inches='tight')
#            k = k +1
#    else:
#        data_plot = summary_data.copy()
#        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
#        plt.figure()
#        figure = data_plot.plot(style=styles,linewidth=1.3)
#        figure.yaxis.set_major_formatter(formatter_billionsinteger)
#        figure.xaxis.label.set_visible(False)
#        plt.title("Daily Net Payment By "+attribute_groupby+" in USD Billions\n(Average in Parentheses)",fontsize=20)
#        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
##        plt.rcParams.update({'font.size': 12})
#        fig = figure.get_figure()
#        fig.set_size_inches(10, 8)
#        fig.savefig(plot_folder+"/History_Chart_By_NetPayments_"+attribute_groupby+".png",bbox_inches='tight')
    
