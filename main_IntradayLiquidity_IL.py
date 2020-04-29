# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 16:01:25 2017
Analyze treasury common deposits file
@author: e620927
"""
################# Setting Up Parameter #################
SYSTEM_INITIATION = False
PRODUCTION_ENVRIONMENT = True

##new column names
column_name_transaction_time = "TRANSACTION_DATE_TIME_GMT"
column_name_transaction_amount = "DER_TRANSACTION_AMOUNT_USD"
column_name_transaction_amount_local = "TRANSACTION_AMOUNT"
column_name_transaction_type = "TRANSACTION_TYPE"
column_name_legal_entity = "MATERIAL_ENTITY"
column_name_datamart = "SOURCEDATAMART"
column_name_currency = "CURRENCY_CODE"
column_name_account_type = "ACCOUNT_TYPE"
column_name_agent_bank_name = "AGENT_BANK_NAME"
column_name_fmu = "FMU"
column_name_running_total = "RUNNING_TOTAL"
column_name_nostro_code = "IBS_NOSTRO_NAME"
column_name_hourminue = "TimeMinute"
column_name_hour = "TimeBucket"
column_name_15minutes = "Time15Minute"
column_name_30minutes = "Time30Minute"
column_name_60minutes = "Time60Minute"

#balance_type = column_name_transaction_amount
balance_type = column_name_transaction_amount_local
currency_major = ["EUR","GBP","JPY","CAD","CHF","CNY","AUD","USD","IDR","BRL"]
#LNNCP threshold
limit_yellow_withfed = 5E9
limit_red_withfed = 3E9
limit_red_nofed = -11.9E9

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
    start_date = datetime.datetime.strptime('2018-09-28 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
    end_date = datetime.datetime.strptime('2018-09-28 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
#    start_date = datetime.datetime.strptime('2018-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.strptime('2018-01-04 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
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
    timewindows = [[x] for x in timewindow]
################# Finish --- Parameter #################

################# Global Libraries #################
import os
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.rcParams.update({'figure.max_open_warning': 0})
from matplotlib.ticker import FuncFormatter
import subprocess
import imp
#import matplotlib.transforms as mtransforms
from pandas.tseries.offsets import BMonthEnd
################# Local Libraries #################
os.chdir(code_dir)
# Load local functions
import UpdateDatabase_Intraday_DB_IL
imp.reload(UpdateDatabase_Intraday_DB_IL)
from UpdateDatabase_Intraday_DB_IL import read_db, update_daily_tables, update_fx_tables
import process_IntradayLiquidity_IL
imp.reload(process_IntradayLiquidity_IL)
from process_IntradayLiquidity_IL import update_table1, update_table3, update_table4#, update_table_SoD_balance
import Functions_Analysis
imp.reload(Functions_Analysis)
from Functions_Analysis import process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST, create_unique_dirname

#   last_update = "20180829"
update_daily_tables()
update_fx_tables()
#update_table_SoD_balance()

if SYSTEM_INITIATION:
    update_table4() #need an hour to update the percentile tables. Need to update on weekly or monthly basis.
elif PRODUCTION_ENVRIONMENT:
    update_table1()
    update_table3()

    start_date = max(read_db("IL_DER_TRANSACTION_AMOUNT_USD_By_FMU_and_TRANSACTION_TYPE_and_ACCOUNT_TYPE_and_CURRENCY_CODE").columns[4:])
#    start_date = "20180628"
    all_dates = read_db("IL_"+balance_type+"_By_FMU_and_TRANSACTION_TYPE_and_ACCOUNT_TYPE_and_CURRENCY_CODE").columns[4:]
    timewindows = [[x] for x in all_dates[all_dates > start_date]]
    if len(timewindows) == 0:
        timewindows = [[max(read_db("Fed_Balance").columns)]]
        
#    timewindows = [[max(read_db("IL_DER_TRANSACTION_AMOUNT_USD_By_FMU_and_TRANSACTION_TYPE_and_ACCOUNT_TYPE_and_CURRENCY_CODE").columns[4:])]]
#    start_date = datetime.datetime.strptime('2018-08-17 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
#    end_date = datetime.datetime.today()     # historical data end date - later than benchmark date
#    timewindows = [[(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d")] for x in range((end_date-start_date).days+1)]

# create folder hierarchy
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)
    
################# formats and styles #################
pd.options.mode.chained_assignment = None
#plt.style.use('ggplot')
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
myFmt = mdates.DateFormatter('%H:%M %p')

#################### Finish Configuration ####################

#################### Start Analysis ####################
start_time = time.time()

for timewindow in timewindows:
    
    day = datetime.date.today().strftime("%Y%m%d")
    plot_folder = output_dir+"/Output_"+day
    plot_folder = create_unique_dirname(plot_folder)
    
    if not os.path.exists(plot_folder):
        os.mkdir(plot_folder)
    
    if False:
        def plot_cumulative_balance(tmp,title=None):
#            tmp = data_plot
            from cycler import cycler
            plt.style.use('default')
            plt.rc('lines', linewidth=3)
            custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
            
            fig, ax = plt.subplots()
            if title is not None:
                tmp.dropna().plot(ax=ax,title=title)
            else:
                tmp.dropna().plot(ax=ax)
            ax.yaxis.set_major_formatter(formatter_millions)
            ax.tick_params(labelsize=15)
            ax.xaxis.set_major_formatter(myFmt)
            ax.xaxis.label.set_visible(False)
            ax.set_prop_cycle(custom_cycler)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            plt.axhline(y=0, linewidth=1, color='#969696',linestyle='--')

            fig.set_size_inches(12,9)
            return(fig)
        
        def calculate_cumulative_position(tmp_data, date):
            tmp_data.index = tmp_data.index-datetime.timedelta(days=(datetime.datetime.strptime(date,"%Y%m%d").date()-datetime.date(1900, 1, 15)).days)
            tmp_data[column_name_transaction_time] = tmp_data.index
            
            data_tmp_nobalance = tmp_data.groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
            data_tmp_nobalance[column_name_running_total] = data_tmp_nobalance[column_name_transaction_amount].cumsum()    
            return(data_tmp_nobalance[column_name_running_total])
        
        def plot_cumulative_transactions(tmp_data, date, title=""):
            return(plot_cumulative_balance(calculate_cumulative_position(tmp_data, date)),title)
#            tmp_data.index = tmp_data.index-datetime.timedelta(days=(datetime.datetime.strptime(date,"%Y%m%d").date()-datetime.date(1900, 1, 15)).days)
#            tmp_data[column_name_transaction_time] = tmp_data.index
#            data_tmp_nobalance = tmp_data.groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
#            data_tmp_nobalance[column_name_running_total] = data_tmp_nobalance[column_name_transaction_amount].cumsum()    
#            
#            lnncp = min(data_tmp_nobalance[column_name_running_total])
#            lpncp = max(data_tmp_nobalance[column_name_running_total])
#            
#            lnncp_time = data_tmp_nobalance[data_tmp_nobalance[column_name_running_total] == lnncp].index[0]
#            lpncp_time = data_tmp_nobalance[data_tmp_nobalance[column_name_running_total] == lpncp].index[0]
#            fig, ax = plt.subplots()
#            data_tmp_nobalance[column_name_running_total].dropna().plot(ax=ax,style=styles)
##            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#        #    if limit_red_nofed is not None:
#        #        ax.fill_between(data_tmp_nobalance[column_name_running_total].index, 0, 1, where=data_tmp_nobalance[column_name_running_total] < limit_red_nofed, facecolor='red', alpha=0.2, transform=trans)
#        #        ax.axhline(y=limit_red_nofed,linewidth=2,zorder=0,color='red')
#        #        ax.text(0.1, 0.1,'Red Limit: '+str(formatter_billions(limit_red_nofed)),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
#            ax.axhline(y=lnncp,linewidth=2,zorder=0,color='mediumvioletred')
#            ax.text(0.85, 0.9,"LPNCP: " + str(round(lpncp/1e9,1))  + "/Time: "+ lpncp_time.strftime("%H:%M"),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
#            ax.text(0.85, 0.1,"LNNCP: " + str(round(lnncp/1e9,1)) + "/Time: "+ lnncp_time.strftime("%H:%M") ,horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
#            ax.yaxis.set_major_formatter(formatter_millions)
#            ax.tick_params(labelsize=15)
#            ax.xaxis.set_major_formatter(myFmt)
#    #        custom_tick_locs = [datetime.time(hour=x) for x in [0,8,9,12,14,15,16,17,18,19]]
#    #        plt.xticks(custom_tick_locs,rotation=90)
#            ax.xaxis.label.set_visible(False)
##            ax.set_title("Running Total Balance "+date+": " + file_suffix,fontsize=20)
#            fig.set_size_inches(12,9)
#            return(plot_cumulative_balance(data_tmp_nobalance[column_name_running_total]))

        table_name = "DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST"
        data_tmp = read_db(table_name,timewindow)
        if len(data_tmp) <= 100:
            print("Skip")
            continue
        
        attribute_groupby = [column_name_transaction_type,column_name_nostro_code]
        table_name = "IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)
        nostro_data = read_db(table_name)
        
        start_date = datetime.datetime.strptime('2018-08-06 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
        end_date = datetime.datetime.strptime('2018-08-10 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date
        timewindow = [(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range((end_date-start_date).days+1)]

        data_tmp = read_db("DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST",timewindow)
        data_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(data_tmp, need_date=True)

        currency = "JPY"
        currency = "GBP"
        currency = "CAD"
        currency = "EUR"
        currencies = ["JPY","GBP","CAD","EUR"]
        for currency in currencies:
            mapping_by_currency = data_tmp.loc[data_tmp[column_name_currency] == currency,[column_name_nostro_code,column_name_account_type,column_name_agent_bank_name,column_name_legal_entity]].drop_duplicates()
            mapping_by_currency.sort_values([column_name_legal_entity,column_name_agent_bank_name]).to_excel(plot_folder+"/Mapping_Nostro_by_"+currency+".xlsx",index=False)
            
    #        data_tmp[data_tmp[column_name_currency] == currency].groupby(column_name_nostro_code).aggregate(column_name_transaction_amount).apply(np.nansum)
    #        nostro_data_currency = nostro_data[nostro_data.index.get_level_values(0).isin(mapping_by_currency[column_name_nostro_code])]
    #        for nostro in mapping_by_currency[column_name_nostro_code]:
    ##            nostro = "NOSTJPY01"
    ##            nostro_data_currency = nostro_data[nostro_data.index.get_level_values(0).isin([nostro])]
    ##            nostro_data_currency.transpose().plot()
    #
    #            fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_nostro_code] == nostro], day)
    #            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+nostro+".png",bbox_inches='tight')
    #            plt.clf()
            
            if currency == "JPY":
                for nostro in ["JPYNOSTRO","OMNIJPYHSBC","OMNIJPYFUJI","JPYFXC"]:
#                    nostro = "OMNIJPYBTMU"
                    fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_nostro_code] == nostro], day)
                    fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+nostro+".png",bbox_inches='tight')
                    plt.clf()
            elif currency == "GBP":
                for nostro in ["BOERESERVEGBP","OMNIGBPBOE","3793EURGBP","SSBLDNGBP"]:
    #                    nostro = "OMNIJPYBTMU"
                    fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_nostro_code] == nostro], day)
                    fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+nostro+".png",bbox_inches='tight')
                    plt.clf()
            elif currency == "CAD":
                for nostro in ["CDSNOSTROCAD1","OMNICADFD","RBCNOSTROCAD1"]:
    #                    nostro = "CDSNOSTROCAD1"
                    fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_nostro_code] == nostro], day)
                    fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+nostro+".png",bbox_inches='tight')
                    plt.clf()
                tmp = pd.DataFrame({
                    "CDSNOSTROCAD1":calculate_cumulative_position(data_tmp[data_tmp[column_name_nostro_code] == "CDSNOSTROCAD1"], day),\
                    "OMNICADFD":calculate_cumulative_position(data_tmp[data_tmp[column_name_nostro_code] == "OMNICADFD"], day),\
                    "RBCNOSTROCAD1":calculate_cumulative_position(data_tmp[data_tmp[column_name_nostro_code] == "RBCNOSTROCAD1"], day)})
                tmp = tmp.fillna(method='ffill').fillna(0)
                
                plot_cumulative_balance(tmp)
                
            elif currency == "EUR":
                    
                for nostro in ["TGTEUR01","NOSTEUR01","NOSTEUR02","PRIMARYEUR"]:
    #                    nostro = "OMNIJPYBTMU"
                    fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_nostro_code] == nostro], day)
                    fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+nostro+".png",bbox_inches='tight')
                    plt.clf()
#                fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_nostro_code].isin(["JPYNOSTRO","OMNIJPYHSBC","OMNIJPYFUJI"])], day)
#                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_HK.png",bbox_inches='tight')
#                plt.clf()
            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB&T - Canada")], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_Canada.png",bbox_inches='tight')
            plt.clf()
            
            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB&T - USA")], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_USA.png",bbox_inches='tight')
            plt.clf()

            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB&T - Hong Kong")], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_HK.png",bbox_inches='tight')
            plt.clf()
            
            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB&T - London")], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_London.png",bbox_inches='tight')
            plt.clf()
            
            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB GmbH")], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_GmbH.png",bbox_inches='tight')
            plt.clf()
            
            fig = plot_cumulative_transactions(data_tmp[data_tmp[column_name_currency] == currency], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+".png",bbox_inches='tight')
            plt.clf()

            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB&T - London")&(data_tmp[column_name_account_type].isin(["SEC"]))], day)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_London_SEC.png",bbox_inches='tight')
            plt.clf()

#            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]!="SSB GmbH")], day)
#            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_nonGmbH.png",bbox_inches='tight')
#            plt.clf()
#    
#            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_account_type].isin(["PRI","DPP"]))], day)
#            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_PRIDPP.png",bbox_inches='tight')
#            plt.clf()
#    
#            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(~data_tmp[column_name_account_type].isin(["PRI","DPP"]))], day)
#            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_nonPRIDPP.png",bbox_inches='tight')
#            plt.clf()
#            
#            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]!="SSB GmbH")&(data_tmp[column_name_account_type].isin(["PRI","DPP"]))], day)
#            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_SSBT_PRIDPP.png",bbox_inches='tight')
#            plt.clf()
#
#            fig = plot_cumulative_transactions(data_tmp[(data_tmp[column_name_currency] == currency)&(data_tmp[column_name_legal_entity]=="SSB GmbH")&(data_tmp[column_name_account_type].isin(["PRI","DPP"]))], day)
#            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+day+"_"+currency+"_GmbH_PRIDPP.png",bbox_inches='tight')
#            plt.clf()
    
            nostro_data_currency = nostro_data[nostro_data.index.get_level_values(0).isin(mapping_by_currency[column_name_nostro_code])]
            nostro_data_currency.groupby(level=[0]).apply(np.nansum)
            nostro_data_currency.transpose().plot()
        
    #STT Corp
    attribute_groupby = [column_name_transaction_type]
    table_name = "IL_"+column_name_transaction_amount+"_By_"+ "_and_".join(attribute_groupby)  #need to be in USD equivalent
    
    summary_data = read_db(table_name)
    if len(summary_data) == 0:
        exit("No file found for " + table_name)
    
    summary_data = summary_data.transpose()
    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    
    data_plot = summary_data
    data_plot = data_plot[["CREDIT","DEBIT"]]
    data_plot['Net'] = data_plot['CREDIT'] + data_plot['DEBIT'] 
    
    data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
    
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
#    attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_currency]
    attributes = [column_name_fmu]

    for attribute in attributes:
#        attribute = attributes[0]
#        attribute_groupby = [attribute,column_name_transaction_type,column_name_currency]
        attribute_groupby = [column_name_transaction_type, attribute]
    
        table_name = "IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)
        
        summary_data = read_db(table_name)
        if len(summary_data) == 0:
            continue
        
        summary_data = summary_data.transpose()
        summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
        
        sub_categorys = summary_data.columns.get_level_values(attribute).drop_duplicates().tolist()
        for sub_category in sub_categorys:
    #        sub_category = 'CAD_OTHERS'
    #        sub_category = 'SSBT NEW YORK'
            
            data_plot = summary_data[sub_category]
            if not any(data_plot.columns=="CREDIT")&any(data_plot.columns=="DEBIT"):
                continue
            data_plot = data_plot[["CREDIT","DEBIT"]]
            data_plot['Net'] = data_plot['CREDIT'] + data_plot['DEBIT'] 
    
            data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
            if balance_type == column_name_transaction_amount:
                fig = plot_type1(data_plot,title = "Daily Credit/Debit Payments for "+sub_category+" in USD Billions\n(Average in Parentheses)")
            else:
                fig = plot_type1(data_plot,title = "Daily Credit/Debit Payments for "+sub_category+" in Local Currency\n(Average in Parentheses)")
                
            fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')

    ## Analyze running total
    
    attribute_groupby = [column_name_transaction_type, column_name_fmu]
    table_name = "IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby)
    summary_data = read_db("IL_"+balance_type+"_By_"+ "_and_".join(attribute_groupby))
    summary_data = summary_data.transpose()
    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    
    Running = read_db("IL_RUNNINGTOTAL_"+balance_type)
    
    ### read start of day balance
    # USD equivalent balance will always be read and used for STT total
    sod_balance_usd = read_db("SoD_Balance_International")
    sod_balance_usd["STT-Total"] = sod_balance_usd.apply(np.nansum,axis=1)

    # SOD balance will feed for each FMU depending on the choice of currencies
    if balance_type == column_name_transaction_amount:
        sod_balance = read_db("SoD_Balance_International")
    elif balance_type == column_name_transaction_amount_local:
        sod_balance = read_db("SoD_Balance_International_Local_Currency")
        
    sod_balance["STT-Total"] = sod_balance.apply(np.nansum,axis=1)
    ##Running.shape
    ##Running.index
#    Running.head()
    ##Running.fillna()
    ##Running['STT-Total'].plot()
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
        tmp.columns = [tmp.columns[0] + "("+ str(billions(p50)) + "/" + str(billions(p75)) + "/" + str(billions(p95))+"/" + str(billions(p99))+")"]
        
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
        
        plt.legend(loc="best",prop={'size':10})
        fig.set_size_inches(12,9)
        return(fig)
        
    def extract_net_cumulative_obligation(running_tmp):
        if all(np.isnan(running_tmp)):
            return(np.nan)
        return(running_tmp.dropna()[-1])
    
    sub_categories = Running.columns
    for sub_category in sub_categories:
    #    sub_category = "GBP_CHAPSandCREST"
#        result_tmp = Running[sub_category].resample('1D').apply([extract_lnncp,extract_lnncp_time,extract_lpncp,extract_lpncp_time])
        if sub_category == "Date":
            continue
        running_tmp = Running[[sub_category,'Date']]
        unique_dates = sorted(running_tmp['Date'].drop_duplicates())
        
        result_tmp = pd.DataFrame()
        for unique_date in unique_dates:
    #        unique_date = unique_dates[1]
            tmp = running_tmp[running_tmp['Date']== unique_date]
            tmp = tmp.drop("Date",axis=1)
            tmp = tmp.apply([extract_lnncp,extract_lnncp_time,extract_lpncp,extract_lpncp_time,extract_net_cumulative_obligation])
            tmp.columns = [unique_date]
            
            if len(result_tmp) == 0:
                result_tmp = tmp
            else:
                result_tmp = result_tmp.join(tmp)
    
        result_tmp = result_tmp.transpose()
        result_tmp.columns = ['LNNCP','LNNCP_Time','LPNCP','LPNCP_Time',"NetCumulativeObligation"]
        result_tmp = result_tmp.dropna()
        
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
        result_tmp["50th Percentile of LNNCP"] = p50
        result_tmp["25th Percentile of LNNCP"] = p25
        result_tmp["5th Percentile of LNNCP"] = p5

        fig = plot_lnncp(result_tmp[[stat_type]],p50,p25,p5,p1,title="Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 25th, 5th and 1st Percentiles")
        fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
        plt.clf()

        fig = plot_lnncp_time(result_tmp,title="Timing of LNNCP and LPNCP for " + sub_category)
        fig.savefig(plot_folder+"/Historical_Trend_"+sub_category.replace(" ","")+"_Timing.png",bbox_inches='tight')
        plt.clf()
        
        if sub_category in sod_balance.columns:
            # Calculate minimum balance and plot the chart
            result_tmp = result_tmp.join(sod_balance[sub_category],how="left")
            result_tmp = result_tmp[~pd.isnull(result_tmp[sub_category])]
            result_tmp["MinimumBalance"] = result_tmp["LNNCP"] + result_tmp[sub_category]
            result_tmp.rename(columns={sub_category:"StartBalance"},inplace=True)
            fig = plot_type1(result_tmp[["LNNCP","StartBalance","MinimumBalance"]],title = "Key Trends for " + sub_category)
            fig.savefig(plot_folder+"/Historical_Trend_Statistics_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
            plt.clf()
            
            stat_type = 'MinimumBalance'
            result_tmp[[stat_type]] = result_tmp[[stat_type]].astype(float)
            p50 = np.nanpercentile(result_tmp[[stat_type]],50)
            p25 = np.nanpercentile(result_tmp[[stat_type]],25)
            p5 = np.nanpercentile(result_tmp[[stat_type]],5)
            p1 = np.nanpercentile(result_tmp[[stat_type]],1)
            result_tmp["50th Percentile of Minimum Balance"] = p50
            result_tmp["25th Percentile of Minimum Balance"] = p25
            result_tmp["5th Percentile of Minimum Balance"] = p5

            fig = plot_lnncp(result_tmp[[stat_type]],p50,p25,p5,p1,title="Historical Trend of "+stat_type+" for " + sub_category + "\nwith 50th, 25th, 5th and 1st Percentiles")
            fig.savefig(plot_folder+"/Historical_Trend_"+stat_type+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
            plt.clf()
            
            # verify EoD balance and SoD balance
            result_tmp['EndBalance'] = result_tmp['StartBalance'] + result_tmp["NetCumulativeObligation"]
            result_tmp['Diff To T+1 SoD Balance'] = result_tmp['StartBalance'].shift(-1) - result_tmp['EndBalance']
            fig = plot_type1(result_tmp[['Diff To T+1 SoD Balance',"EndBalance"]],title = "Reconciliation of EoD and SoD Balance for " + sub_category)
            fig.savefig(plot_folder+"/Historical_Trend_Reconciliation_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
            plt.clf()
        
        if sub_category in sod_balance.columns:
            result_tmp = result_tmp.join(summary_data[sub_category])
            result_tmp["NET"] = result_tmp["CREDIT"] + result_tmp["DEBIT"]
            result_tmp["Balance Turnover Ratio"] = result_tmp["CREDIT"]/result_tmp["StartBalance"]
#            result_tmp[["NetCumulativeObligation","LNNCP","MinimumBalance"]].plot()
#            result_tmp[["NetCumulativeObligation","LNNCP","MinimumBalance"]].corr(result_tmp[["NetCumulativeObligation","LNNCP","MinimumBalance"]])
        result_tmp.to_excel(plot_folder+"/LNNCP_LPNCP_SOB_EOD_Timing_Recon"+sub_category.replace(" ","")+".xlsx")

    #################### Analyze specific day's data #########
    #plot with and without beginning balance
    def plot2(tmp,title=None,flag=False,yformatter = formatter_billions):
#       tmp = data_tmp_nobalance[column_name_running_total].dropna()
        from cycler import cycler
        plt.style.use('default')
        plt.rc('lines', linewidth=3)
        custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
        
        fig, ax = plt.subplots()
        tmp.dropna().plot(ax=ax)
        if title is not None:
            plt.title(title, fontsize=20)
        ax.yaxis.set_major_formatter(yformatter)
        ax.tick_params(labelsize=15)
        ax.xaxis.set_major_formatter(myFmt)
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
        
    def plot3(tmp,red_corridor="1th Percentile",title=None,yformatter = formatter_billions):
#            tmp = data_tmp_nobalance_with_corridor
        from cycler import cycler
        plt.style.use('default')
        plt.rc('lines', linewidth=1)
        custom_cycler = cycler(color=['#0055ad', '#14beff', '#e28100','#fccc00','#679000','#aabc00','#7f00af','#7676aa'])
        
        fig, ax = plt.subplots()
        tmp.iloc[:,0].dropna().plot(ax=ax,color="black",linewidth=2)
        if title is not None:
            plt.title(title, fontsize=20)

        tmp.iloc[:,1:].dropna().plot(ax=ax,style=styles2,alpha=0.5)
#            trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
#            ax.fill_between(tmp[column_name_running_total].index, 0, 1, where=tmp[column_name_running_total] < tmp[red_corridor], facecolor='red', alpha=0.2, transform=trans)
        ax.yaxis.set_major_formatter(yformatter)
        ax.tick_params(labelsize=15)
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.label.set_visible(False)
        ax.set_prop_cycle(custom_cycler)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        plt.axhline(y=0, linewidth=1, color='#969696',linestyle='--')
        fig.set_size_inches(12,9)
        return(fig)
        
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
        lnncp_time = lnncp_time.strftime("%H:%M:%S")
#            lpncp = max(net_cumulative)
#            lpncp_time = net_cumulative[net_cumulative == lpncp].index[0]
        
        if starting_balance is not None:
            Start_balance = starting_balance
            ending_balance = net_cumulative[-1] + Start_balance
            minimum_balance = lnncp + starting_balance
            result = pd.DataFrame({"":[date,formatter_millions(Start_balance),formatter_millions(ending_balance),formatter_millions(minimum_balance),lnncp_time,end_of_month,formatter_millions(lnncp)]})
            result.index = ["Date","Starting Balance","Ending Balance","Minimum Balance","Time","End-of-Month","LNNCP"]
            return(result)
        else:
            result = pd.DataFrame({"":[date,formatter_millions(lnncp),lnncp_time,end_of_month]})
            result.index = ["Date","LNNCP","Time","End-of-Month"]
            return(result)

    def analyze_intraday_data(tmp_data,file_suffix,key,limit_red_nofed = None, fed_balance = None,balance_type=column_name_transaction_amount):
    #        tmp_data = data_tmp[data_tmp["FMU"]==fmu]
    #          file_suffix = fmu.replace(" ", "")
    #        tmp_data = data_tmp.copy()
    #    file_suffix = "ALL_US_Transactions"
        #key = fmu
    #    fed_balance = Fed_balance.loc[date,'Fed_Balance']
        if len(tmp_data) == 0:
            return()
        
        ###Running total analysis
        tmp_data.index = tmp_data.index-datetime.timedelta(days=(datetime.datetime.strptime(date,"%Y%m%d").date()-datetime.date(1900, 1, 15)).days)
        tmp_data[column_name_transaction_time] = tmp_data.index
#        tmp_data.head()
#        tmp_data.columns
        
        data_tmp_nobalance = tmp_data.groupby(column_name_transaction_time).agg({balance_type:sum})
        data_tmp_nobalance[column_name_running_total] = data_tmp_nobalance[balance_type].cumsum()
        
        fig = plot2(data_tmp_nobalance[column_name_running_total].dropna(),title="Net Cumulative Balance "+date+": " + file_suffix,flag=True)
        fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()

        if fed_balance is not None:
            fig = plot2(data_tmp_nobalance[column_name_running_total].add(fed_balance).dropna(),title="Running Total Balance "+date+": " + file_suffix,flag=True)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+".png",bbox_inches='tight')
            plt.clf()
        
        ## with corridor
        table_name = "IL_RUNNINGTOTAL_"+balance_type+"_"+key
        percentiles_runningtotal = read_db(table_name)
        
        if len(percentiles_runningtotal) >0:
            data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].join(percentiles_runningtotal)
            fig = plot3(data_tmp_nobalance_with_corridor,title ="Net Cumulative Balance "+date+" with Percentiles: " + file_suffix)
            fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
            plt.clf()
            data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_net_cumulative_balance_"+date+"_"+file_suffix+"_with_corridor.xlsx")
     
        if fed_balance is not None:
            table_name = "IL_RUNNINGTOTAL_"+balance_type+"_with_FedBalance_"+key
            percentiles_runningtotal = read_db(table_name)

            if len(percentiles_runningtotal) >0:
                data_tmp_nobalance_with_corridor = data_tmp_nobalance[[column_name_running_total]].add(fed_balance).join(percentiles_runningtotal)
                
                fig = plot3(data_tmp_nobalance_with_corridor,title ="Running Total Balance "+date+" with Percentiles: " + file_suffix)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_with_fed_balance_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
                data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_running_balance_"+date+"_"+file_suffix+"_with_corridor.xlsx")
        try:
            #through put graphs
            data_tmp_credit = tmp_data[tmp_data[column_name_transaction_type] == "CREDIT"].groupby(column_name_transaction_time).agg({balance_type:sum})
            data_tmp_debit = tmp_data[tmp_data[column_name_transaction_type] == "DEBIT"].groupby(column_name_transaction_time).agg({balance_type:sum})
            data_tmp_credit[column_name_running_total] = data_tmp_credit[balance_type].cumsum()
            data_tmp_debit[column_name_running_total] = data_tmp_debit[balance_type].cumsum()
            
            #abosolute amount: combined
            thoughput_data = pd.DataFrame({"Credit Throughput":data_tmp_credit[column_name_running_total],"Debit Throughput":(-1*data_tmp_debit[column_name_running_total])})
            fig = plot2(thoughput_data,title="Throughput Analysis "+date+": " + file_suffix,flag=False)
            fig.savefig(plot_folder+"/IntradayLiquidity_throughput_amount_"+date+"_"+file_suffix+".png",bbox_inches='tight')
            plt.clf()

            #abosolute amount: credit
            table_name = "IL_RUNNINGTOTAL_"+balance_type+"_CREDIT_"+key
            percentiles_runningtotal = read_db(table_name)
        
            if len(percentiles_runningtotal) >0:
                data_tmp_nobalance_with_corridor = data_tmp_credit[[column_name_running_total]].join(percentiles_runningtotal,how="left")
                fig = plot3(data_tmp_nobalance_with_corridor,title ="Throughput Analysis for Credit Transactions for "+file_suffix +": "+date)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_credit_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
                plt.clf()
                data_tmp_nobalance_with_corridor.index = [x.time() for x in data_tmp_nobalance_with_corridor.index]
                data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_running_total_by_credit_"+date+"_"+file_suffix+"_with_corridor.xlsx")
                
            #abosolute amount: debit
            table_name = "IL_RUNNINGTOTAL_"+balance_type+"_DEBIT_"+key
            percentiles_runningtotal = read_db(table_name)
        
            if len(percentiles_runningtotal) >0:
                data_tmp_nobalance_with_corridor = data_tmp_debit[[column_name_running_total]].join(percentiles_runningtotal,how="left")
                fig = plot3(-1*data_tmp_nobalance_with_corridor,red_corridor="99th Percentile",title ="Throughput Analysis for Debit Transactions for "+file_suffix +": "+date)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_debit_"+date+"_"+file_suffix+"_with_corridor.png",bbox_inches='tight')
                plt.clf()
                data_tmp_nobalance_with_corridor.index = [x.time() for x in data_tmp_nobalance_with_corridor.index]
                (-1*data_tmp_nobalance_with_corridor).to_excel(plot_folder+"/IntradayLiquidity_running_total_by_debit_"+date+"_"+file_suffix+"_with_corridor.xlsx")

            #### Percentages
            throughput_credit = data_tmp_credit[column_name_running_total]/max(data_tmp_credit[column_name_running_total])
            throughput_debit = data_tmp_debit[column_name_running_total]/min(data_tmp_debit[column_name_running_total])
            #percentage : combined
            thoughput_data = pd.DataFrame({"Credit Throughput":throughput_credit,"Debit Throughput":throughput_debit})
            fig = plot2(thoughput_data,title="Throughput Analysis "+date+": " + file_suffix,flag=False,yformatter=formatter_percentages)
            fig.savefig(plot_folder+"/IntradayLiquidity_throughput_amount_"+date+"_"+file_suffix+".png",bbox_inches='tight')
            plt.clf()

            #percentage: credit
            table_name = "IL_RUNNINGTOTAL_"+balance_type+"_CREDIT_"+key+"_Percentage"
            percentiles_runningtotal = read_db(table_name)
        
            if len(percentiles_runningtotal) >0:
                data_tmp_nobalance_with_corridor = thoughput_data[['Credit Throughput']].join(percentiles_runningtotal,how="left").fillna(method='ffill').fillna(method='backfill')
                fig = plot3(data_tmp_nobalance_with_corridor,title ="Throughput Analysis for Credit Transactions for "+file_suffix +": "+date,yformatter=formatter_percentages)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_credit_"+date+"_"+file_suffix+"_with_corridor_Percentage.png",bbox_inches='tight')
                plt.clf()
                data_tmp_nobalance_with_corridor.index = [x.time() for x in data_tmp_nobalance_with_corridor.index]
                data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_running_total_by_credit_"+date+"_"+file_suffix+"_with_corridor_Percentage.xlsx")
            #percentage: debit
            table_name = "IL_RUNNINGTOTAL_"+balance_type+"_DEBIT_"+key+"_Percentage"
            percentiles_runningtotal = read_db(table_name)
        
            if len(percentiles_runningtotal) >0:
                data_tmp_nobalance_with_corridor = thoughput_data[['Debit Throughput']].join(percentiles_runningtotal,how="left").fillna(method='ffill').fillna(method='backfill')
                fig = plot3(data_tmp_nobalance_with_corridor,red_corridor="99th Percentile",title ="Throughput Analysis for Debit Transactions for "+file_suffix +": "+date,yformatter=formatter_percentages)
                fig.savefig(plot_folder+"/IntradayLiquidity_running_total_by_debit_"+date+"_"+file_suffix+"_with_corridor_Percentage.png",bbox_inches='tight')
                plt.clf()
                data_tmp_nobalance_with_corridor.index = [x.time() for x in data_tmp_nobalance_with_corridor.index]
                data_tmp_nobalance_with_corridor.to_excel(plot_folder+"/IntradayLiquidity_running_total_by_debit_"+date+"_"+file_suffix+"_with_corridor_Percentage.xlsx")
        except:
            print("Throughput is not graphed")
        
        file_name = plot_folder+"/IntradayLiquidity_statistics_"+date+"_"+file_suffix+".tex"
        stats = daily_statistics(data_tmp_nobalance[column_name_running_total], starting_balance=fed_balance)
        stats.to_latex(file_name,longtable=True)
        return(stats)

#    Fed_balance = read_db("SoD_Balance_International")
#    Fed_balance.index = [x.to_pydatetime() for x in Fed_balance.index]
#    Fed_balance["STT-Total"] = Fed_balance.apply(np.nansum,axis=1)
    
    sod_balance.index = [x.to_pydatetime() for x in sod_balance.index]
    sod_balance_usd.index = [x.to_pydatetime() for x in sod_balance_usd.index]

    table_name = "DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST"
    AsOfDates = []
    for date in timewindow:
    #    date = timewindow[0]
        data_tmp = read_db(table_name,date)
        if len(data_tmp) <= 100:
            print("Skip: " + date)
            continue
        AsOfDates.append(date)
        # process table
        data_tmp = process_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST(data_tmp, need_date=True)

        if date in sod_balance.index:
            analyze_intraday_data(data_tmp.copy(),file_suffix="STT-Total",key="STT-Total",limit_red_nofed=None, fed_balance=sod_balance_usd.loc[date,'STT-Total'])
        else:
            analyze_intraday_data(data_tmp.copy(),file_suffix="STT-Total",key="STT-Total")
    #    analyze_intraday_data(data_tmp,file_suffix="ALL_US_Transactions",key="STT-Total",limit_red_nofed=limit_red_nofed)
    #    analyze_intraday_data(data_tmp,"ALL_US_Transactions","STT-Total",limit_red_nofed)
    
#        fmus = data_tmp["FMU"].drop_duplicates().tolist()
        fmus = ['EUR_London_DB','EUR_GmbH_DB','EUR_GmbH_ISP',\
        'JPY_BTMU',\
        'GBP_CHAPSandCREST',\
        'CAD_LVTS','CAD_FD']
        
        stats = pd.DataFrame()
        for fmu in fmus:
    #        fmu = fmus[3]
            if fmu in sod_balance.columns and date in sod_balance.index:
                stat = analyze_intraday_data(data_tmp[data_tmp["FMU"]==fmu],file_suffix=fmu.replace(" ", ""),key=fmu,fed_balance=sod_balance.loc[date,fmu],balance_type=balance_type)
            else:
                stat = analyze_intraday_data(data_tmp[data_tmp["FMU"]==fmu],file_suffix=fmu.replace(" ", ""),key=fmu,balance_type=balance_type)
            stat.columns = [fmu]
            if len(stats) == 0:
                stats = stat
            else:
                stats = stats.join(stat,how="outer")
        stats.to_latex(plot_folder+"/IntradayLiquidity_Stats_LE_"+date+".tex",longtable=True)
        stats.to_excel(plot_folder+"/IntradayLiquidity_Stats_LE_"+date+".xlsx")

        currencies = currency_major
#        for currency in currencies:
#            analyze_intraday_data(data_tmp[data_tmp[column_name_currency]==currency],file_suffix=currency.replace(" ", ""),key=currency)
#
        les = data_tmp[column_name_legal_entity].drop_duplicates().tolist()
#        for le in les:
#    #        fmu = fmus[3]
#            analyze_intraday_data(data_tmp[data_tmp[column_name_legal_entity]==le],le.replace(" ", "").replace("&",""),key=le)

#################### Finish analysis and start reporting ########################
#    AsOfDates = ["20180808"]
    if len(AsOfDates) != 0:
        AsOfDates = [datetime.datetime.strptime(x, "%Y%m%d") for x in AsOfDates]
        today = max(AsOfDates).strftime("%Y/%m/%d")
        AsOfDates = [x.strftime("%Y%m%d") for x in sorted(AsOfDates,reverse=True)]
        ### Execute PDF report
        file = open(pdf_dir + "/GlobalParameters.tex", "w")
        command="\\newcommand\\Output{"+plot_folder+"}\n"+\
        "\\newcommand\\AsOfDate{"+today +"}\n"+\
        "\\newcommand\\AsOfDates{"+','.join(AsOfDates)+"}\n"+\
        "\\newcommand\\Total{STT-Total}\n"+\
        "\\newcommand\\FMUs{"+','.join(fmus)+"}\n"+\
        "\\newcommand\\Currencies{"+','.join(sorted(currencies))+"}\n"+\
        "\\newcommand\\LegalEntity{"+','.join(sorted([x.replace(" ", "").replace("&","") for x in les]))+"}\n"+\
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
