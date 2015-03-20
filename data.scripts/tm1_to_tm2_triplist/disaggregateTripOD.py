#'  Script to convert Travel Model One (TM1) trip lists into synthetic Travel Model Two (TM2) trip lists.
#'  Each TAZ in the TM1 has the MAZs contained within (centroid based) as alternatives.
#'  A size-term-based probability array is computed and a Monte Carlo selection of TM2 MAZ is performed. 
#'  
#'  The user has to specify the following parameters
#'  @param sizeCoefficientsFile: csv file that holds the size coefficients (borrowed from TM1 model)
#'  @param mazDataFile: TM2 MAZ data file
#'  @param MAZ_to_TM1TAZ_xwalk: TM2 MAZ to TM1 TAZ
#'  @param householdsFile: Household data from TM1 100% run
#'  @param geographicCWalkFile: Crosswalk between different TM2 geographies
#'  @param inputTripFile: Trip list from TM1 100% run
#'  @param outputTripFile: File name of output trip list
#'  @param jointFlag: [True/False] Logical variable indicating whether the trip list being processed is joint or individual
#'        
#'  @date: 2014-04-14
#'  @author: sn, narayanamoorthys AT pbworld DOT com

import numpy as np
import pandas as pd
import gc
from time import strftime
import itertools as iterT
from collections import OrderedDict

########################################################################################################
#Inputs
########################################################################################################
sizeCoefficientsFile = 'data/SizeCoefficients_for_disaggregation.csv'
mazDataFile = 'data/mazDataRevised_Step2.csv'
MAZ_to_TM1TAZ_xwalk = 'data/MAZ_to_TM1_TAZ.csv'
householdsFile = 'data/householdData_3.csv'
geographicCWalkFile = 'data/geographicCWalk.csv'
inputTripFile = 'data/indivTripData_3.csv'
outputTripFile = 'indivTripData_3.csv'
jointFlag = False

########################################################################################################
#Function definitions
########################################################################################################

#Monte Carlo prediction function
def MonteCarlo(zoneGroupObject): 
    cumPROB = mazCumPROB[zoneGroupObject.name[0]][zoneGroupObject.name[1]]
    i = np.searchsorted(cumPROB.values, zoneGroupObject.values, side='left')
    return cumPROB.index[i]

#Defining income categories based on TM1
def incomeCat(incomeInDollars):
    "low: [-Inf,30k), med: [30k,60k), high: [60k,100k), very high: [100k,+Inf)"
    if incomeInDollars < 30000:
        incCat = 'low'
    elif (incomeInDollars>=30000) & (incomeInDollars<60000):
        incCat = 'med'
    elif (incomeInDollars>=60000) & (incomeInDollars<100000):
        incCat = 'high'
    else:
        incCat = 'very high'
    return incCat

#Segmenting trip purpose
def segTripPurpose(tripPurpose, incCat):
    "work: low, med, high, very high"
    if tripPurpose.lower() == 'work':
        segTripPurpose = tripPurpose.lower() + '_' + incCat
    else:
        segTripPurpose = tripPurpose
    return segTripPurpose

########################################################################################################
# Pre-computing probability arrays 
########################################################################################################
print strftime("%Y-%m-%d %H:%M:%S"), ':Pre-computing probability arrays...'
#Read in the size-term coefficient data and index it on trip purpose segments
#Sample query: sizeCoeff.loc['escort'].loc['kids']
sizeCoeff = pd.read_csv(sizeCoefficientsFile)
sizeCoeff = sizeCoeff.set_index(['purpose','segment'])

#Read in the employment data 
mazData = pd.read_csv(mazDataFile)
geographicCWalk = pd.read_csv(geographicCWalkFile)
mazData.drop(['MAZ','TAZ','TAZ_ORIGINAL'], axis=1, inplace=True)

#Updating MAZ and TAZ fields in MAZ data file with sequential zone numbering
mazData = pd.merge(mazData, geographicCWalk, left_on='MAZ_ORIGINAL', right_on='MAZ_ORIGINAL', how='left')

#Read in TM1 TAZ to TM2 MAZ cross-walk
#Drop MAZs not contained in TM1 zone system
tm1crosswalk = pd.read_csv(MAZ_to_TM1TAZ_xwalk)
tm1crosswalk = tm1crosswalk.dropna(subset=['TAZ1454'], how='any') 

#Update TM2 MAZ data with TM1 zone numbers (right_join) -> MAZs that are not contained in TM1 TAZ is dropped
mazData = pd.merge(mazData, tm1crosswalk, left_on='MAZ_ORIGINAL', right_on='MAZ_ORIGINAL', how='right')

#Collapse socio-demographic and employment data into size-term categories
sizeData = mazData.loc[:,('TAZ','MAZ','TAZ1454')]

__temp_val = mazData.eval('HH')
sizeData['TOTHH'] = __temp_val

__temp_val = mazData.eval('emp_personal_svcs_retail + emp_retail')
sizeData['RETEMPN'] = __temp_val

__temp_val = mazData.eval('emp_prof_bus_svcs')
sizeData['FPSEMPN'] = __temp_val

__temp_val = mazData.eval('emp_amusement + emp_restaurant_bar + emp_pvt_ed_post_k12_oth + emp_public_ed + emp_health + emp_hotel + emp_personal_svcs_retail')
sizeData['HEREMPN'] = __temp_val

__temp_val = mazData.eval('emp_const_non_bldg_prod + emp_state_local_gov_ent + emp_prof_bus_svcs')
sizeData['OTHEMPN'] = __temp_val

__temp_val = mazData.eval('emp_ag + emp_const_non_bldg_prod')
sizeData['AGREMPN'] = __temp_val

__temp_val = mazData.eval('emp_whsle_whs + emp_mfg_prod + emp_trans + emp_utilities_prod')
sizeData['MWTEMPN'] = __temp_val

__temp_val = mazData.eval('EnrollGrade9to12')
sizeData['HSENROLL'] = __temp_val

__temp_val = mazData.eval('collegeEnroll')
sizeData['COLLFTE'] = __temp_val

__temp_val = mazData.eval('otherCollegeEnroll + AdultSchEnrl')
sizeData['COLLPTE'] = __temp_val

__temp_val = 0
sizeData['AGE0519'] = 0

__temp_val = mazData.eval('emp_total')
sizeData['TOTEMP'] = __temp_val

sizeData = sizeData.set_index(['TAZ1454','MAZ'])

#Declaring dictionaries to hold the arrays with purpose segments as keys
mazSIZE = {} #Each element holds a pandas.core.Series with size terms 
tazSIZE = {} #Each element holds a pandas.core.Series with TAZ size totals
mazPROB = {} #Each element holds a pandas.core.Series with probabilities
mazCumPROB = {} #Each element holds a pandas.core.Series with cumulative probabilities sorted on MAZ# within TAZ

#Iterate over different trip purpose segments and compute the probability within each TAZ
for index, row in sizeCoeff.iterrows():
    #Collect the size coefficients in a pandas.core.Series
    beta = sizeCoeff.loc[index[0]].loc[index[1]]

    #Determine the market segment being processed
    if index[0] == index[1]:
        tripPurpose = str(index[0])
    else:
        tripPurpose = str(index[0]) + '_' + str(index[1])
        
    #Determine the MAZ size totals
    #Update MAZ groups with zero size to a small value (0.001) so as to assign equal probability
    mazSIZE[tripPurpose] = sizeData.mul(beta, axis=1).sum(axis = 1)
    idx = mazSIZE[tripPurpose].groupby(level='TAZ1454').filter(lambda grp: (grp.sum()) == 0).index
    mazSIZE[tripPurpose].ix[idx] = 0.001

    #Determine the TAZ size totals
    tazSIZE[tripPurpose] = mazSIZE[tripPurpose].groupby(level = 'TAZ1454').sum()

    #Determine the MAZ probability and cumulative probabilities
    mazPROB[tripPurpose] = mazSIZE[tripPurpose].div(tazSIZE[tripPurpose], level = 0)
    mazCumPROB[tripPurpose] = mazPROB[tripPurpose][mazPROB[tripPurpose]>0].sort_index().groupby(level = 'TAZ1454').cumsum()

########################################################################################################
# Preparing trip list for simulation
########################################################################################################
print strftime("%Y-%m-%d %H:%M:%S"), ':Preparing trip list for simulation...'
#Household Data
hhData = pd.read_csv(householdsFile)
hhData['INC_CAT'] = hhData['income'].apply(incomeCat)
hhData = hhData.loc[:,('hh_id','INC_CAT')]

#Read in the trip List
tripList = pd.read_csv(inputTripFile).reset_index()
tripList = tripList.query('trip_mode < 9')

#Determine trip purpose segmentation
tripList = pd.merge(tripList, hhData, left_on='hh_id', right_on='hh_id', how='left')
tripList['OPURP'] = np.vectorize(segTripPurpose)(tripList['orig_purpose'],tripList['INC_CAT'])
tripList['DPURP'] = np.vectorize(segTripPurpose)(tripList['dest_purpose'],tripList['INC_CAT'])

#Random number generation
np.random.seed(0)
tripList['uRandDrawO'] = pd.Series(np.random.uniform(low=0.0, high=1.0, size=len(tripList)), index=tripList.index)
tripList['uRandDrawD'] = pd.Series(np.random.uniform(low=0.0, high=1.0, size=len(tripList)), index=tripList.index)
n = gc.collect()

########################################################################################################
# Monte Carlo prediction
########################################################################################################
print strftime("%Y-%m-%d %H:%M:%S"), ':Starting Monte Carlo prediction...'
tripList['OMAZ'] = tripList.groupby(['OPURP', 'orig_taz'])['uRandDrawO'].transform(MonteCarlo)
tripList['DMAZ'] = tripList.groupby(['DPURP', 'dest_taz'])['uRandDrawD'].transform(MonteCarlo)
print strftime("%Y-%m-%d %H:%M:%S"), ':Completed Monte Carlo prediction...'

########################################################################################################
# Post-processing - Updating TM1 fields to TM2 
########################################################################################################
print strftime("%Y-%m-%d %H:%M:%S"), ':Preparing file for output...'

#Dictionary mapping TM1 to TM2 purpose
purposeMap = { 'atwork_business' : 'Work-Based'
                ,'atwork_eat' : 'Work-Based'
                ,'atwork_maint' : 'Work-Based'
                ,'eatout' : 'Eating Out'
                ,'escort_kids' : 'Escort'
                ,'escort_no kids' : 'Escort'
                ,'othdiscr' : 'Discretionary'
                ,'othmaint' : 'Maintenance'
                ,'school_grade' : 'School'
                ,'school_high' : 'School'
                ,'shopping' : 'Shop'
                ,'social' : 'Visiting'
                ,'university' : 'University'
                ,'work_high' : 'Work'
                ,'work_low' : 'Work'
                ,'work_med' : 'Work'
                ,'work_very high' : 'Work'}

#Dictionary mapping TM1 to TM2 time periods
timePeriodMap = {5 : 2
                    ,6 : 3
                    ,7 : 4
                    ,8 : 5
                    ,9 : 10
                    ,10 : 12
                    ,11 : 14
                    ,12 : 16
                    ,13 : 18
                    ,14 : 20
                    ,15 : 22
                    ,16 : 24
                    ,17 : 26
                    ,18 : 28
                    ,19 : 30
                    ,20 : 32
                    ,21 : 34
                    ,22 : 36
                    ,23 : 38
                    ,24 : 40}

#Dictionary mapping TM1 to TM2 modes
modeMap = {1 : 1
            ,2 : 2
            ,3 : 3
            ,4 : 5
            ,5 : 6
            ,6 : 8
            ,7 : 9
            ,8 : 10
            ,9 : 11
            ,10 : 11
            ,11 : 11
            ,12 : 11
            ,13 : 11
            ,14 : 12
            ,15 : 12
            ,16 : 12
            ,17 : 12
            ,18 : 12}

#Updating TM1 trip list fields to match TM2 values
tripList['orig_purpose'] = tripList['orig_purpose'].apply(lambda x: purposeMap.get(x, x)) 
tripList['dest_purpose'] = tripList['dest_purpose'].apply(lambda x: purposeMap.get(x, x)) 
tripList['tour_purpose'] = tripList['tour_purpose'].apply(lambda x: purposeMap.get(x, x)) 
tripList['trip_mode'] = tripList['trip_mode'].apply(lambda x: modeMap.get(x, x)) 
tripList['tour_mode'] = tripList['tour_mode'].apply(lambda x: modeMap.get(x, x)) 
tripList['depart_hour'] = tripList['depart_hour'].apply(lambda x: timePeriodMap.get(x, x)) 

#Drop all transit trips as we would need to predict boarding and alighting TAP information
tripList = tripList.loc[~tripList['trip_mode'].isin([11,12,13]),:]

#Adding additional fields that are in TM2 trip list and setting them to zero
tripList['trip_board_tap'] = 0
tripList['trip_alight_tap'] = 0
tripList['set'] = -1
tripList['TRIP_TIME'] = 0
tripList['TRIP_DISTANCE'] = 0
tripList['TRIP_COST'] = 0

#Dictionary mapping TM1 to TM2 trip column names
if jointFlag == True:
    columnMap = OrderedDict([('hh_id', 'hh_id')
            ,('tour_id', ' tour_id')
            ,('stop_id', 'stop_id')
            ,('inbound', 'inbound')
            ,('tour_purpose', 'tour_purpose')
            ,('orig_purpose', 'orig_purpose')
            ,('dest_purpose', 'dest_purpose')
            ,('OMAZ', 'orig_mgra')
            ,('DMAZ', 'dest_mgra')
            ,('parking_taz', 'parking_mgra')
            ,('depart_hour', 'stop_period')
            ,('trip_mode', 'trip_mode')
            ,('trip_mode', 'trip_mode')
            ,('num_participants', 'num_participants')
            ,('trip_board_tap', 'trip_board_tap')
            ,('trip_alight_tap', 'trip_alight_tap')
            ,('tour_mode', 'tour_mode')
            ,('set', 'set')
            ,('TRIP_TIME', 'TRIP_TIME')
            ,('TRIP_DISTANCE', 'TRIP_DISTANCE')
            ,('TRIP_COST', 'TRIP_COST')])
else:
    columnMap = OrderedDict([('hh_id', 'hh_id')
            ,('person_id', 'person_id')
            ,('person_num', 'person_num')
            ,('tour_id', ' tour_id')
            ,('stop_id', 'stop_id')
            ,('inbound', 'inbound')
            ,('tour_purpose', 'tour_purpose')
            ,('orig_purpose', 'orig_purpose')
            ,('dest_purpose', 'dest_purpose')
            ,('OMAZ', 'orig_mgra')
            ,('DMAZ', 'dest_mgra')
            ,('parking_taz', 'parking_mgra')
            ,('depart_hour', 'stop_period')
            ,('trip_mode', 'trip_mode')
            ,('trip_board_tap', 'trip_board_tap')
            ,('trip_alight_tap', 'trip_alight_tap')
            ,('tour_mode', 'tour_mode')
            ,('set', 'set')
            ,('TRIP_TIME', 'TRIP_TIME')
            ,('TRIP_DISTANCE', 'TRIP_DISTANCE')
            ,('TRIP_COST', 'TRIP_COST')])

tripList = tripList.rename(columns=columnMap)
tripList = tripList.sort('index').drop('index',1)
tripList = tripList[columnMap.values()]

print strftime("%Y-%m-%d %H:%M:%S"), ':Writing out csv file...'
##Writing out TM2 trip list
tripList.to_csv(outputTripFile, index=False)
print strftime("%Y-%m-%d %H:%M:%S"), ':Complete!'