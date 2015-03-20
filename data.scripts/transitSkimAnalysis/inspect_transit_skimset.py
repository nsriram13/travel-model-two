# @author: Sriram Narayanamoorthy 
# @email: narayanamoorthys@pbworld.com
# @date: 2014-10-26
#
# Script to analyse transit skim sets produced by MTC TM2
# Uses NumPy and SciPy libraries
# Pandas used for creating formatted reports

import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd
import eucledian_distance_matrix as dist
from time import strftime

########################################################################################################
#Inputs
########################################################################################################
#Setting file paths and other parameters
TAP_COUNT=6214
period_token = '@@PERIOD@@'
set_token = '@@SET@@'
skim_token = '@@SKIM@@'
infile = r'skims_raw/csv_new/ts_' + period_token + '_' + set_token + '.csv'
pd.set_option('precision',3)
periods = ['EA','AM','MD','PM','EV']
sets = ['SET1','SET2','SET3']
skims_masterList = (['COMPCOST','IWAIT','XWAIT','XPEN','BRDPEN','XFERS','FARE','XWTIME','AEWTIME','LB_TIME','EB_TIME','LR_TIME','HR_TIME','CR_TIME','BEST_MODE'])

########################################################################################################
#Function definitions
########################################################################################################
#Function to load skims to memory
def loadSkim(periods, sets, skims, verbose=True):
    '''
    Loads the skimsets specified by period, set, skims into memory
    INPUT: period - List; set - List; skims - List
    OUTPUT: dict[(period,set,skim)]
    '''
    transit_skims = {}
    for period in periods:
        for set in sets:
            skim_matrix_set = pd.read_csv(infile.replace(period_token,period).replace(set_token,set), names=['row', 'column', 'matrix']+skims_masterList, header=None)
            for skim in skims:
                if verbose:
                    print strftime("%Y-%m-%d %H:%M:%S"), ':Loading skims into memory: ' + period + ', ' + set + ', ' + skim
                a = np.zeros((TAP_COUNT, TAP_COUNT))
                a[skim_matrix_set['row']-1, skim_matrix_set['column']-1] = skim_matrix_set[skim]
                transit_skims[(period,set,skim)] = csr_matrix(a)
    return transit_skims

#Function to calculate matrix statistics
def getMatrixStatistics(skim_matrix):
    '''
    Computes several descriptive statistics of the matrix.
    INPUT - dict[(period,set,skim)] - Object coming out of loadSkim function
    OUTPUT - pd.DataFrame: MIN,MAX,MEAN,VARIANCE,% NON-ZERO
    '''
    if skim_matrix.nnz == 0:
            a = pd.DataFrame(np.vstack((0.00,0.00,0.00,0.00,0.00)).T
             , columns=['MIN','MAX','MEAN','VARIANCE','% NON-ZERO'])
    else:
        MIN = np.min(skim_matrix.data)
        MAX = np.max(skim_matrix.data)
        MEAN = np.mean(skim_matrix.data)
        VARIANCE = np.var(skim_matrix.data)
        NNZ = (float(skim_matrix.data.shape[0])/(TAP_COUNT**2))*100
        a = pd.DataFrame(np.vstack((MIN,MAX,MEAN,VARIANCE,NNZ)).T, columns=['MIN','MAX','MEAN','VARIANCE','% NON-ZERO'])
    return a

########################################################################################################
#Reports
########################################################################################################
#Load all skims to memory
#NOTE: Requires a ton of memory - alternatively this method can be called to load one skim at a time within the calculation loops. Lower memory cost but slow.
transit_skims = loadSkim(periods,sets,skims_masterList, True)

#Descriptive statistics for all matrices
report = {}
for skim in skims_masterList:
    print strftime("%Y-%m-%d %H:%M:%S"), ':Computing statistics for ' + skim
    report_period = {}
    for period in periods:
        report_set = {}
        for set in sets:
            report_set[set] = getMatrixStatistics(transit_skims[(period,set,skim)])
            report_set[set]['SET'] = set
        report_period[period] = pd.concat([report_set['SET1'],report_set['SET2'],report_set['SET3']],axis=0)
        report_period[period]['TIME_PERIOD'] = period
    report[skim] = pd.concat([report_period['EA'],report_period['AM'],report_period['MD'],report_period['PM'],report_period['EV']],axis=0)
    report[skim]['SKIM'] = skim
    report[skim] = report[skim].set_index(['TIME_PERIOD'])
pd.concat([report['COMPCOST'] , report['IWAIT'] , report['XWAIT'] 
           , report['XPEN'] , report['XFERS'] , report['FARE'] 
           , report['XWTIME'] , report['AEWTIME'] , report['LB_TIME'] 
           , report['EB_TIME'] , report['LR_TIME'] , report['HR_TIME'] 
           , report['CR_TIME'] , report['BEST_MODE']],axis=0).to_csv('./reports/stats.csv')

#Create distance frequency distribution of for TAP pairs with 0 paths
report = {}
for period in periods:
    report_set = {}
    for set in sets:
        tnet_skim = transit_skims[(period,set,'COMPCOST')].A
        distance = np.floor(dist.tap_dist).astype(int)
        #distance[tnet_skim != 0] = nan
        
        #Flatten the array and count the number of TAP pairs within specific distance bins
        y = np.bincount(np.reshape(distance[tnet_skim != 0], len(distance[tnet_skim != 0])))
        ii = np.nonzero(y)[0]
        
        print strftime("%Y-%m-%d %H:%M:%S"), ':Computed distance frequency distribution for ' + period + ' skim ' + set
        report_set[set] = pd.DataFrame(np.vstack((ii,y[ii], (y[ii].astype(float)/sum(y).astype(float))*100)).T, columns=['Distance Bin',period+set, period+set+'%'])
        report_set[set] = report_set[set].set_index('Distance Bin')
    report[period] = pd.concat([report_set['SET1'],report_set['SET2'],report_set['SET3']],axis=1)
    #report[period] = report[period].set_index('Distance Bin')
pd.concat([report['EA'],report['AM'],report['MD'],report['PM'],report['EV']],axis=1).to_csv('./reports/zeroDistFreq.csv')