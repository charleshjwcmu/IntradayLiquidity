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
    output_dir = "Z:/Charles/IntradayLiquidity/Output_Common"
    pdf_dir = "Z:/Charles/IntradayLiquidity/PDFReport_Common"
    TEST_ENVIRONMENT = False
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=1)
else:
    code_dir = "Z:/Charles/IntradayLiquidity/SourceCodes"
    output_dir = "Z:/Charles/IntradayLiquidity/Output_Test"
    pdf_dir = "Z:/Charles/IntradayLiquidity/PDFReport_Test"
    TEST_ENVIRONMENT = True

#Setup parameters
if TEST_ENVIRONMENT:
    start_date = datetime.datetime.strptime('2018-06-25 00:00:00', '%Y-%m-%d %H:%M:%S')   # historical data start date - before benchmark date
    end_date = datetime.datetime.strptime('2018-06-29 00:00:00', '%Y-%m-%d %H:%M:%S')     # historical data end date - later than benchmark date

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
import UpdateDatabase_Intraday_DB
imp.reload(UpdateDatabase_Intraday_DB)
from UpdateDatabase_Intraday_DB import read_db, UPDATE_BCBS_248_Data_Extract_A1_Report
import process_IntradayLiquidity
imp.reload(process_IntradayLiquidity)
from process_IntradayLiquidity import update_table1, update_table2

if not TEST_ENVIRONMENT:
    UPDATE_BCBS_248_Data_Extract_A1_Report()
    update_table1()
    update_table2()
import Functions_Analysis
imp.reload(Functions_Analysis)
from Functions_Analysis import process_bcbs_extract_a1_report, create_unique_dirname

if False:
    ###update Domestic tables
    from UpdateDatabase_Intraday_DB import UPDATE_BCBS_248_Data_Extract_A1_Report
    UPDATE_BCBS_248_Data_Extract_A1_Report()
    
    ###update International tables
    from UpdateDatabase_Intraday_DB import UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST
    UPDATE_DB_DM_RPT_IDLM_A1_TRANSACTION_SUMMARY_DETAIL_HIST()

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

#LNNCP threshold
limit_yellow_withfed = 5E9
limit_red_withfed = 3E9
limit_red_nofed = -11.9E9

timewindow = [(end_date - datetime.timedelta(days=x)).strftime("%Y%m%d") for x in range((end_date-start_date).days+1)]

#################### Process Horizontal Data #########
balance_type = column_name_transaction_amount
###Netpayment
attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_fmu,column_name_transaction_type]

for attribute_groupby in attributes:
#    attribute_groupby = column_name_legal_entity
#    attribute_groupby = column_name_hour
#    attribute_groupby = column_name_fmu
#    attribute_groupby = column_name_datamart
#    attribute_groupby = column_name_transaction_type

    table_name = balance_type+"_By_"+ attribute_groupby
    
    summary_data = read_db(table_name)
    if len(summary_data) == 0:
        continue
    
    summary_data = summary_data.transpose()
    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    
    if summary_data.shape[1] >= 8:
        k = 1
        for i in range(0,summary_data.shape[1],4):
            data_plot = summary_data.iloc[:,i:(i+4)].copy()
            data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
            plt.figure()
            figure = data_plot.plot(style=styles,linewidth=1.3)
            figure.yaxis.set_major_formatter(formatter_billionsinteger)
            figure.xaxis.label.set_visible(False)
            plt.title("Daily Net Payment By "+attribute_groupby+" in USD Billions\n(Average in Parentheses)",fontsize=20)
            plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
#            plt.rcParams.update({'font.size': 12})
            fig = figure.get_figure()
            fig.set_size_inches(10, 8)
            fig.savefig(plot_folder+"/History_Chart_By_NetPayments_"+attribute_groupby+"_"+str(k)+".png",bbox_inches='tight')
            k = k +1
    else:
        data_plot = summary_data.copy()
        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
        plt.figure()
        figure = data_plot.plot(style=styles,linewidth=1.3)
        figure.yaxis.set_major_formatter(formatter_billionsinteger)
        figure.xaxis.label.set_visible(False)
        plt.title("Daily Net Payment By "+attribute_groupby+" in USD Billions\n(Average in Parentheses)",fontsize=20)
        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
#        plt.rcParams.update({'font.size': 12})
        fig = figure.get_figure()
        fig.set_size_inches(10, 8)
        fig.savefig(plot_folder+"/History_Chart_By_NetPayments_"+attribute_groupby+".png",bbox_inches='tight')
    
###Gross Payment by Credit/Debit
balance_type = column_name_transaction_amount
attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_fmu]
for attribute in attributes:
#    attribute = column_name_legal_entity
    #attribute = column_name_hour
    #attribute = column_name_fmu
    attribute_groupby = [column_name_transaction_type, attribute]
    
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
        data_plot['Net'] = data_plot['CREDIT'] + data_plot['DEBIT'] 

        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(billionsinteger))]
        plt.figure()
        figure = data_plot.plot(style=styles,linewidth=1.3)
        figure.yaxis.set_major_formatter(formatter_billionsinteger)
        figure.xaxis.label.set_visible(False)
        plt.title("Daily Credit/Debit Payments for "+sub_category+" in USD Billions\n(Average in Parentheses)",fontsize=20)
        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
#        plt.rcParams.update({'font.size': 12})
        fig = figure.get_figure()
        fig.set_size_inches(10, 8)
        fig.savefig(plot_folder+"/History_Chart_By_TotalPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')
    
### Stat
attributes = [column_name_legal_entity,column_name_datamart,column_name_hour,column_name_fmu,column_name_transaction_type]
for attribute in attributes:
#    attribute = column_name_fmu
#    attribute = column_name_hour

    attribute_groupby = [column_name_transaction_type,attribute]
    table_name = 'Stat_'+balance_type+"_By_"+ "_and_".join(attribute_groupby)
    
    summary_data = read_db(table_name)
    if len(summary_data) == 0:
        continue
    summary_data = summary_data.transpose()
    summary_data.index = [datetime.datetime.strptime(x,"%Y%m%d") for x in summary_data.index]
    sub_categories = summary_data.columns.get_level_values(attribute).drop_duplicates().tolist()
    
    for sub_category in sub_categories:
        #    sub_category = sub_categories[5]
        
        data_plot = summary_data[sub_category]['CREDIT']
#        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(formatter_millions))]
        plt.figure()
        figure = data_plot.loc[:,['maximum','percentile_99','percentile_95','std','average','percentile_5','percentile_1','minimum']].plot(style=styles,linewidth=1.3)
        figure.yaxis.set_major_formatter(formatter_millionsinteger)
        figure.xaxis.label.set_visible(False)
        plt.title("Statistics For "+ sub_category+"'s Credit Transactions in USD Millions",fontsize=20)
        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
#        plt.legend(loc='best',prop={'size':10})
#        plt.rcParams.update({'font.size': 20})
        fig = figure.get_figure()
        fig.set_size_inches(10, 8)
        fig.savefig(plot_folder+"/Statistics_By_TotalCreditPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')

        data_plot = summary_data[sub_category]['DEBIT']
#        data_plot.columns=[a_+"("+b_+")" for a_, b_ in zip(data_plot.columns, data_plot.apply(np.nanmean,axis=0).map(formatter_millions))]
        plt.figure()
        figure = data_plot.loc[:,['maximum','percentile_99','percentile_95','std','average','percentile_5','percentile_1','minimum']].plot(style=styles,linewidth=1.3)
        figure.yaxis.set_major_formatter(formatter_millionsinteger)
        figure.xaxis.label.set_visible(False)
        plt.title("Statistics For "+ sub_category+"'s Debit Transactions in USD Millions",fontsize=20)
        plt.legend(loc=2, bbox_to_anchor=(1,0.8),prop={'size':10})
#        plt.rcParams.update({'font.size': 12})
        fig = figure.get_figure()
        fig.set_size_inches(10, 8)
        fig.savefig(plot_folder+"/Statistics_By_TotalDEBITPayments_"+attribute+"_"+sub_category.replace(" ","")+".png",bbox_inches='tight')

#################### Analyze specific day's data #########

#plot with and without beginning balance
def analyze_intraday_data(tmp_data,file_suffix,limit_red_nofed = None):
#        tmp_data = data_tmp[data_tmp["FMU"]==fmu]
#        tmp_data = data_tmp[data_tmp["CLEARING_MATERIAL_ENTITY"]==le]
#        tmp_data = data_tmp
    data_tmp_nobalance = tmp_data.groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
    data_tmp_nobalance["RUNNING_TOTAL"] = data_tmp_nobalance[column_name_transaction_amount].cumsum()
    
    fig, ax = plt.subplots()
    data_tmp_nobalance[column_name_transaction_amount].dropna().plot(ax=ax,style=styles)
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.yaxis.set_major_formatter(formatter_billions)
    ax.tick_params(labelsize=20)
    ax.xaxis.label.set_visible(False)
    ax.set_title("Net Flow  "+date+": " + file_suffix,fontsize=20)
    fig.set_size_inches(12,9)
    fig.savefig(plot_folder+"/IntradayLiquidity_transaction_"+date+"_"+file_suffix+".png",bbox_inches='tight')
    plt.clf()

    lnncp = min(data_tmp_nobalance["RUNNING_TOTAL"])
    lpncp = max(data_tmp_nobalance["RUNNING_TOTAL"])
    
    lnncp_time = data_tmp_nobalance[data_tmp_nobalance["RUNNING_TOTAL"] == lnncp].index[0]
    lpncp_time = data_tmp_nobalance[data_tmp_nobalance["RUNNING_TOTAL"] == lpncp].index[0]
    
    fig, ax = plt.subplots()
    data_tmp_nobalance["RUNNING_TOTAL"].dropna().plot(ax=ax,style=styles)
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    if limit_red_nofed is not None:
        ax.fill_between(data_tmp_nobalance["RUNNING_TOTAL"].index, 0, 1, where=data_tmp_nobalance["RUNNING_TOTAL"] < limit_red_nofed, facecolor='red', alpha=0.5, transform=trans)
        ax.axhline(y=limit_red_nofed,linewidth=2,zorder=0,color='red')
        ax.text(0.1, 0.1,'Red Limit: '+str(formatter_billions(limit_red_nofed)),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)

    ax.axhline(y=lpncp,linewidth=2,zorder=0,color='green')
    ax.axhline(y=lnncp,linewidth=2,zorder=0,color='mediumvioletred')
    ax.text(0.85, 0.9,"LPNCP: " + str(round(lpncp/1e9,1))  + "/Time: "+ lpncp_time.strftime("%H:%M"),horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)
    ax.text(0.85, 0.1,"LNNCP: " + str(round(lnncp/1e9,1)) + "/Time: "+ lnncp_time.strftime("%H:%M") ,horizontalalignment='center',verticalalignment='center',transform = ax.transAxes,size=13)

    ax.yaxis.set_major_formatter(formatter_billions)
    ax.tick_params(labelsize=20)
    ax.xaxis.label.set_visible(False)
    ax.set_title("Running Total Balance "+date+": " + file_suffix,fontsize=20)
    fig.set_size_inches(12,9)
    fig.savefig(plot_folder+"/IntradayLiquidity_running_total_"+date+"_"+file_suffix+".png",bbox_inches='tight')
    plt.clf()
    
    #through put graphs
    data_tmp_credit = tmp_data[tmp_data[column_name_transaction_type] == "CREDIT"].groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
    data_tmp_debit = tmp_data[tmp_data[column_name_transaction_type] == "DEBIT"].groupby(column_name_transaction_time).agg({column_name_transaction_amount:sum})
    data_tmp_credit["RUNNING_TOTAL"] = data_tmp_credit[column_name_transaction_amount].cumsum()
    data_tmp_debit["RUNNING_TOTAL"] = data_tmp_debit[column_name_transaction_amount].cumsum()
    
    throughput_credit = data_tmp_credit["RUNNING_TOTAL"]/max(data_tmp_credit["RUNNING_TOTAL"])
    throughput_debit = data_tmp_debit["RUNNING_TOTAL"]/min(data_tmp_debit["RUNNING_TOTAL"])
    
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
    
    fig.savefig(plot_folder+"/IntradayLiquidity_throughput_"+date+"_"+file_suffix+".png",bbox_inches='tight')
    plt.clf()
    
    for tran_type in ["CREDIT","DEBIT"]:
        value_by_time = tmp_data[tmp_data[column_name_transaction_type] == tran_type].groupby('TimeBucket').aggregate(column_name_transaction_amount).apply(np.nansum)
        vol_by_time = tmp_data[tmp_data[column_name_transaction_type] == tran_type].groupby('TimeBucket').aggregate(column_name_transaction_amount).apply(np.count_nonzero)
        
        plt.figure()
        if tran_type == "CREDIT":
            figure = value_by_time.plot.bar(style=styles,linewidth=1.3,width=0.8)
        else:
            figure = (value_by_time*-1).plot.bar(style=styles,linewidth=1.3,width=0.8)
        figure.yaxis.set_major_formatter(formatter_billionsinteger)
        figure.xaxis.label.set_visible(False)
        plt.title("Transaction Value of Wires By Time Bucket: "+date,fontsize=20)
        fig = figure.get_figure()
        fig.set_size_inches(12,9)
        fig.savefig(plot_folder+"/IntradayLiquidity_WireValueByTime_"+tran_type+"_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()
        
        plt.figure()
        figure = vol_by_time.plot.bar(style=styles,linewidth=1.3,width=0.8)
        figure.xaxis.label.set_visible(False)
        plt.title("Transaction Value of Wires By Time Bucket: "+date,fontsize=20)
        fig = figure.get_figure()
        fig.set_size_inches(12,9)
        fig.savefig(plot_folder+"/IntradayLiquidity_WireVolByTime_Credit_"+tran_type+"_"+date+"_"+file_suffix+".png",bbox_inches='tight')
        plt.clf()
        
table_name = "BCBS_248_Data_Extract_A1_Report"
AsOfDates = []
for date in timewindow:
#    date = timewindow[0]
    data_tmp = read_db(table_name,date)
    if len(data_tmp) <= 100:
        print("Skip: " + date)
        continue
    AsOfDates.append(date)
    # process table
    if table_name == "BCBS_248_Data_Extract_A1_Report":
        data_tmp = process_bcbs_extract_a1_report(data_tmp)
        
#    analyze_intraday_data(data_tmp,"ALL_US_Transactions")
    analyze_intraday_data(data_tmp,"ALL_US_Transactions",limit_red_nofed)
    
    fmus = ['CHIPS','Fedwire Funds','Fedwire Securities','FED CHK','FED ACH']
#    'FED ACH' all happen in 8:30am
    for fmu in fmus:
        analyze_intraday_data(data_tmp[data_tmp["FMU"]==fmu],fmu.replace(" ", ""))
  
    legal_entity = ['SSBT BOSTON','SSBT NEW YORK']
    for le in legal_entity:
        analyze_intraday_data(data_tmp[data_tmp["CLEARING_MATERIAL_ENTITY"]==le],le.replace(" ", ""))

#################### Finish analysis and start reporting ########################
if len(AsOfDates) == 0:
    AsOfDates = [datetime.datetime.strptime(x, "%Y%m%d") for x in AsOfDates]
    today = "N/A"
    AsOfDates = [x.strftime("%Y%m%d") for x in sorted(AsOfDates,reverse=True)]
    ### Execute PDF report
    file = open(pdf_dir + "/GlobalParameters.tex", "w")
    command="\\newcommand\\Output{"+plot_folder+"}\n"+\
    "\\newcommand\\AsOfDate{"+today +"}\n"+\
    "\\newcommand\\AsOfDates{"+','.join(AsOfDates)+"}\n"+\
    "\\newcommand\\FMUs{CHIPS,FedwireFunds,FedwireSecurities}\n"+\
    "\\newcommand\\LE{SSBTBOSTON,SSBTNEWYORK}\n"+\
    "\\newcommand\\TimeBucket{01-02,02-03,03-04,04-05,05-06,06-07,07-08,08-09,09-10,10-11,11-12,12-13,13-14,14-15,15-16,16-17,17-18,18-19,19-20}\n"
    file.write(command)
    file.close()
else:       
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
    "\\newcommand\\TimeBucket{01-02,02-03,03-04,04-05,05-06,06-07,07-08,08-09,09-10,10-11,11-12,12-13,13-14,14-15,15-16,16-17,17-18,18-19,19-20}\n"
    file.write(command)
    file.close()

os.chdir(pdf_dir)
file_name = 'Intradaly Liquidity Risk Monitoring Reporting-'+today.replace('/','') 
pdf_name = file_name+".pdf"
j = 1
while os.path.exists(pdf_name):
    file_name2 = file_name+"-Update"+str(j)
    pdf_name = file_name2+".pdf"
    j = j + 1

subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', file_name, './document_workingcopy.tex'])
subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', file_name, './document_workingcopy.tex'])
subprocess.call(['pdflatex', '-output-directory', "./", '-jobname', file_name, './document_workingcopy.tex'])
