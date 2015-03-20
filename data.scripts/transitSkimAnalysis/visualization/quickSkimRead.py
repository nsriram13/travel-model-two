#'  Read TAP TAP skims and write out csv file with set of accessible destination TAPs and number of XFERS
#'  Helper script for the TAP visualization R script
#'        
#'  @date: 2013-05-09
#'  @author: sn, narayanamoorthys AT pbworld DOT com

import pandas as pd
import numpy as np
from time import strftime
import os, sys

#Specify input file
TAP_QUERY = int(sys.argv[1])
PERIOD = sys.argv[2]
set_token = '@@SET@@'
infile = r'skims\ts_' + PERIOD + '_' + set_token + '.csv'

sets = ['SET1','SET2','SET3']
skims_masterList = (['COMPCOST','IWAIT','XWAIT','XPEN','BRDPEN','XFERS','FARE','XWTIME','AEWTIME','LB_TIME','EB_TIME','LR_TIME','HR_TIME','CR_TIME','BEST_MODE'])

#Pre-declaring data types for columns - makes reading files faster
datatypes = {'OTAP' : np.int64    ,'DTAP' : np.int64    ,'matrix' : np.int64    ,'COMPCOST' : np.float64    ,'IWAIT' : np.float64
    ,'XWAIT' : np.float64    ,'XPEN' : np.int64    ,'BRDPEN' : np.int64    ,'XFERS' : np.int64    ,'FARE' : np.float64
    ,'XWTIME' : np.float64    ,'AEWTIME' : np.float64    ,'LB_TIME' : np.float64    ,'EB_TIME' : np.float64    ,'LR_TIME' : np.float64
    ,'HR_TIME' : np.float64    ,'CR_TIME ' : np.float64    ,'BEST_MODE' : np.int64}

#Function to load skims to memory and write out mini-csvs that R can read fast
def writePlotData(tap,period,sets, verbose=True):
    '''
    Write out data for plotting 
    INPUT: period - char; set - List
    OUTPUT: csv files 'ts_plot_set_period.csv'
    '''
    for set in sets:
        if verbose:
            print strftime("%Y-%m-%d %H:%M:%S"), ':Writing plot file: ' + period + ', ' + set
        skim_matrix_set = pd.read_csv(infile.replace(set_token,set), names=['OTAP', 'DTAP', 'matrix']+skims_masterList, header=None, dtype = datatypes)
        skim_matrix_set[skim_matrix_set['OTAP'] == tap][['DTAP','XFERS']].to_csv(r'plot_csv\ts_plot_' + set + '_' + period + '_' + str(tap) + '.csv', index=False)

writePlotData(TAP_QUERY,PERIOD,sets)

