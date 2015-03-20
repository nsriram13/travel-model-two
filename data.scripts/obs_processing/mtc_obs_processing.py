'''
Mode choice targets development for MTC Travel Model 2 Round 1 Calibration

The process starts with On-Board Survey (OBS) data processing for MTC system-wide transit survey (circa 2014). The survey was conducted individually for each operator listed below:
AC Transit,ACE,Caltrain,County Connection,Golden Gate Transit (bus),Golden Gate Transit (ferry), LAVTA,Napa Vine,Petaluma,SF Bay Ferry,SamTrans,Santa Rosa CityBus,
Sonoma County,Tri-Delta,Union City.

The datasets have been normalized to a unified database. Refer to https://github.com/MetropolitanTransportationCommission/onboard-surveys
for data processing details. Major operators still being surveyed include MUNI, VTA and BART. As an interim 2004 survey datasets are being used (after expanding to 
2010 boardings) for these operators.Additionally, there are operators not being surveyed but being modelled in TM2. For these, the target boardings for year 2010 is 
split by purpose, access mode and auto-sufficiency based on the observed distribution from an operator with very similar characteristics (primarily based on technology 
and total boardings).

The end product of OBS processing is transit trip targets by purpose, technology, access-mode and auto-sufficiency.This data is combined with Household Interview Survey (HIS)
to get the overall trip and tour targets for the multi-modal transportation system in the Bay Area. Since OBS is a choice based sample the data is assumed to be highly reliable 
and is used directly as trip targets for transit modes. However, in order to impute the tour/trip pattern 

Revised mode switching calibration targets were created by holding auto and non-motorized trips constant, and scaling transit trips to match totals by mode and purpose from new OBS 
(non-transit trips on transit tours generated per 3 above).  Tour targets are created holding auto and non-motorized constant from HIS, and scaling the new OBS data from trips to tours 
by applying a trip/tour factor.

@date: 2014-01-23
@author: sn, narayanamoorthys AT pbworld DOT com
'''

import numpy as np
import pandas as pd
from obs_constants import *
pd.set_option('display.precision', 3)
pd.set_option('display.width', 200)

#Read in on board survey datasets. Add binary fields for quick summaries
obs_data = pd.read_csv(r'data\0_SYSTEMWIDE Data\survey.csv', low_memory=False)
obs_data['uno'] = 1
obs_data['sero'] = 0

#Code number of workers
obs_data['workers_int'] = obs_data['workers'].apply(lambda x: worker_crosswalk.get(x, x))
#obs_data['workers_int'].value_counts(dropna=False)
#obs_data['workers'].value_counts(dropna=False)

#Code number of vehicles
obs_data['vehicles_int'] = obs_data['vehicles'].apply(lambda x: vehicles_crosswalk.get(x, x))
#obs_data['vehicles_int'].value_counts(dropna=False)
#obs_data['vehicles'].value_counts(dropna=False)

#Code number of persons
obs_data['persons_int'] = obs_data['persons'].apply(lambda x: persons_crosswalk.get(x, x))
#obs_data['persons_int'].value_counts(dropna=False)
#obs_data['persons'].value_counts(dropna=False)

#Code tour purpose
obs_data['tourPurpAgg'] = obs_data['tour_purp'].apply(lambda x: tour_purp_crosswalk.get(x, x))
obs_data['tourPurpAgg'] = obs_data['tourPurpAgg'].astype('category')
obs_data['tourPurpAgg'] = obs_data['tourPurpAgg'].cat.set_categories(purpose_map.values())
#obs_data['tourPurpAgg'].value_counts(dropna=False)
#obs_data['tour_purp'].value_counts(dropna=False)

#Code anchor access mode
#This is the set of rules used to code mode to/from transit at home end. Three mode options are:
#Walk, PNR, KNR
#All missing values are coded as Walk
obs_data['anchorAccessMode'] = 'Walk'
obs_data.loc[obs_data['access_mode'].isin(['walk']) & ~obs_data['dest_purp'].isin(['home']), 'anchorAccessMode'] = '1_Walk'
obs_data.loc[obs_data['access_mode'].isin(['pnr','bike']) & ~obs_data['dest_purp'].isin(['home']), 'anchorAccessMode']  = '2_PNR'
obs_data.loc[obs_data['access_mode'].isin(['knr']) & ~obs_data['dest_purp'].isin(['home']), 'anchorAccessMode'] = '3_KNR'
obs_data.loc[obs_data['egress_mode'].isin(['walk']) & obs_data['dest_purp'].isin(['home']), 'anchorAccessMode'] = '1_Walk'
obs_data.loc[obs_data['egress_mode'].isin(['pnr','bike']) & obs_data['dest_purp'].isin(['home']), 'anchorAccessMode'] = '2_PNR'
obs_data.loc[obs_data['egress_mode'].isin(['knr']) & obs_data['dest_purp'].isin(['home']), 'anchorAccessMode'] = '3_KNR'
obs_data['anchorAccessMode'] = obs_data['anchorAccessMode'].astype('category')
obs_data['anchorAccessMode'] = obs_data['anchorAccessMode'].cat.set_categories(access_mode_map.values())
#obs_data['anchorAccessMode'].value_counts(dropna=False)

#Define Auto-sufficiency with respect to number of workers
#All missing values are assumed to be zero auto
obs_data['autoSuff'] = '0 Auto'
obs_data.loc[obs_data['auto_suff'].isin(['auto negotiating']), 'autoSuff'] = 'Autos<Workers'
obs_data.loc[obs_data['auto_suff'].isin(['auto sufficient']), 'autoSuff'] = 'Autos>=Workers'
obs_data['autoSuff'] = obs_data['autoSuff'].astype('category')
obs_data['autoSuff'] = obs_data['autoSuff'].cat.set_categories(asuff_map.values())
#obs_data['autoSuff'].value_counts(dropna=False)

#Split operators to local and express where separate targets by boardings is available
obs_data.loc[obs_data['operator'].isin(['AC Transit']) & obs_data['survey_tech'].isin(['local bus']),'operator'] = 'AC Transit [LOCAL]'
obs_data.loc[obs_data['operator'].isin(['AC Transit']) & obs_data['survey_tech'].isin(['express bus']),'operator'] = 'AC Transit [EXPRESS]'
obs_data.loc[obs_data['operator'].isin(['County Connection']) & obs_data['survey_tech'].isin(['local bus']),'operator'] = 'County Connection [LOCAL]'
obs_data.loc[obs_data['operator'].isin(['County Connection']) & obs_data['survey_tech'].isin(['express bus']),'operator'] = 'County Connection [EXPRESS]'
obs_data.loc[obs_data['operator'].isin(['Golden Gate Transit (bus)']) & obs_data['survey_tech'].isin(['local bus']),'operator'] = 'Golden Gate Transit [LOCAL]'
obs_data.loc[obs_data['operator'].isin(['Golden Gate Transit (bus)']) & obs_data['survey_tech'].isin(['express bus']),'operator'] = 'Golden Gate Transit [EXPRESS]'
obs_data.loc[obs_data['operator'].isin(['Napa Vine']) & obs_data['survey_tech'].isin(['local bus']),'operator'] = 'Napa Vine [LOCAL]'
obs_data.loc[obs_data['operator'].isin(['Napa Vine']) & obs_data['survey_tech'].isin(['express bus']),'operator'] = 'Napa Vine [EXPRESS]'
obs_data.loc[obs_data['operator'].isin(['SamTrans']) & obs_data['survey_tech'].isin(['local bus']),'operator'] = 'SamTrans [LOCAL]'
obs_data.loc[obs_data['operator'].isin(['SamTrans']) & obs_data['survey_tech'].isin(['express bus']),'operator'] = 'SamTrans [EXPRESS]'

#Drop weekend records and pre-test records 
mask = obs_data['weekpart'].isin(['WEEKEND']) | obs_data['weight'].isin([1])
obs_data = obs_data.loc[~mask,:]

#Some housekeeping
obs_data = obs_data.sort(['survey_tech', 'tourPurpAgg'])
obs_data.rename(columns={'weight':'boardWeight', 'trip_weight':'tripWeight'}, inplace=True)

#Samples by technology, tour purpose, access mode and auto-sufficiency
pd.pivot_table(obs_data, values='uno', index=['survey_tech', 'tourPurpAgg', 'anchorAccessMode'], columns=['autoSuff'] ,margins=True, aggfunc=np.sum).fillna(0)
#pd.pivot_table(obs_data, values='uno', index=['survey_tech', 'tourPurpAgg', 'anchorAccessMode'], columns=['autoSuff'] ,margins=True, aggfunc=np.sum).fillna(0).to_csv('sample_shares_technology.csv')

#Trips by operator, tour purpose, access mode and auto-sufficiency
pd.pivot_table(obs_data, values='tripWeight', index=['survey_tech', 'tourPurpAgg', 'anchorAccessMode'], columns=['autoSuff'] ,margins=True, aggfunc=np.sum).fillna(0)
#pd.pivot_table(obs_data, values='trip_weight', index=['survey_tech', 'tourPurpAgg', 'anchorAccessMode'], columns=['autoSuff'] ,margins=True, aggfunc=np.sum).fillna(0).to_csv('trip_shares_technology.csv')

#Boardings and trips by operator, tour purpose, access mode and auto-sufficiency
obs_collapsed = obs_data.groupby(['operator', 'tourPurpAgg', 'anchorAccessMode', 'autoSuff'])[['boardWeight','tripWeight']].sum().fillna(0)

'''
BART Data Targets
This comes directly from the 2010 BART summaries.
'''
#BART Data
bart_data = pd.read_csv(r'data\1_BART Data\bart targets.csv', low_memory=False)
bart_data.rename(columns={'purpose':'tourPurpAgg', 'mode':'anchorAccessMode', 'autoSufficiency':'autoSuff', 'trips':'boardWeight'}, inplace=True)
bart_data['tripWeight'] = bart_data['boardWeight'] 

#Updating columns to pd.category type
bart_data.loc[bart_data['tourPurpAgg'].isin(['Work']),'tourPurpAgg'] = '1_WORK'
bart_data.loc[bart_data['tourPurpAgg'].isin(['University']),'tourPurpAgg'] = '2_UNIVERSITY'
bart_data.loc[bart_data['tourPurpAgg'].isin(['School']),'tourPurpAgg'] = '3_SCHOOL'
bart_data.loc[bart_data['tourPurpAgg'].isin(['Indiv Maintanance']),'tourPurpAgg'] = '4_MAINTENANCE'
bart_data.loc[bart_data['tourPurpAgg'].isin(['Joint Maintanance']),'tourPurpAgg'] = '4_MAINTENANCE'
bart_data.loc[bart_data['tourPurpAgg'].isin(['Indiv Discretionary']),'tourPurpAgg'] = '5_DISCRETIONARY'
bart_data.loc[bart_data['tourPurpAgg'].isin(['Joint Discretionary']),'tourPurpAgg'] = '5_DISCRETIONARY'
bart_data.loc[bart_data['tourPurpAgg'].isin(['AtWork']),'tourPurpAgg'] = '6_AT-WORK SUBTOUR'
bart_data['tourPurpAgg'] = bart_data['tourPurpAgg'].astype('category')
bart_data['tourPurpAgg'] = bart_data['tourPurpAgg'].cat.set_categories(purpose_map.values())

bart_data.loc[bart_data['anchorAccessMode'].isin(['Walk']),'anchorAccessMode'] = '1_Walk'
bart_data.loc[bart_data['anchorAccessMode'].isin(['PNR']),'anchorAccessMode'] = '2_PNR'
bart_data.loc[bart_data['anchorAccessMode'].isin(['KNR']),'anchorAccessMode'] = '3_KNR'
bart_data['anchorAccessMode'] = bart_data['anchorAccessMode'].astype('category')
bart_data['anchorAccessMode'] = bart_data['anchorAccessMode'].cat.set_categories(access_mode_map.values())

bart_data.loc[bart_data['autoSuff'].isin(['0 Autos']), 'autoSuff'] = '0 Auto'
bart_data.loc[bart_data['autoSuff'].isin(['Autos<Workers']), 'autoSuff'] = 'Autos<Workers'
bart_data.loc[bart_data['autoSuff'].isin(['Autos>=Workers']), 'autoSuff'] = 'Autos>=Workers'
bart_data['autoSuff'] = bart_data['autoSuff'].astype('category')
bart_data['autoSuff'] = bart_data['autoSuff'].cat.set_categories(asuff_map.values())

#Boardings and trips by operator, tour purpose, access mode and auto-sufficiency
bart_collapsed = bart_data.groupby(['operator', 'tourPurpAgg', 'anchorAccessMode', 'autoSuff'])[['boardWeight','tripWeight']].sum().fillna(0)

'''
2004 MUNI OBS data processing
Data processed by Joel Freedman - refer to Stata script "summarize muni data.do" for details
'''
muni_data = pd.read_csv(r'data\2_MUNI - Boarding Data\MUNI_coded_for_MTC.csv', low_memory=False)
muni_data['uno'] = 1
muni_data['sero'] = 0

#Updating columns to pd.category type
muni_data.loc[muni_data['tourPurpAgg'].isin(['Work']),'tourPurpAgg'] = '1_WORK'
muni_data.loc[muni_data['tourPurpAgg'].isin(['University']),'tourPurpAgg'] = '2_UNIVERSITY'
muni_data.loc[muni_data['tourPurpAgg'].isin(['School']),'tourPurpAgg'] = '3_SCHOOL'
muni_data.loc[muni_data['tourPurpAgg'].isin(['Maintenance']),'tourPurpAgg'] = '4_MAINTENANCE'
muni_data.loc[muni_data['tourPurpAgg'].isin(['Discretionary']),'tourPurpAgg'] = '5_DISCRETIONARY'
muni_data.loc[muni_data['tourPurpAgg'].isin(['At-work Subtour']),'tourPurpAgg'] = '6_AT-WORK SUBTOUR'
muni_data['tourPurpAgg'] = muni_data['tourPurpAgg'].astype('category')
muni_data['tourPurpAgg'] = muni_data['tourPurpAgg'].cat.set_categories(purpose_map.values())

muni_data.loc[muni_data['anchorAccessMode'].isin(['Walk']),'anchorAccessMode'] = '1_Walk'
muni_data.loc[muni_data['anchorAccessMode'].isin(['PNR']),'anchorAccessMode'] = '2_PNR'
muni_data.loc[muni_data['anchorAccessMode'].isin(['KNR']),'anchorAccessMode'] = '3_KNR'
muni_data['anchorAccessMode'] = muni_data['anchorAccessMode'].astype('category')
muni_data['anchorAccessMode'] = muni_data['anchorAccessMode'].cat.set_categories(access_mode_map.values())

muni_data.loc[muni_data['autoSuff'].isin(['0 Autos']), 'autoSuff'] = '0 Auto'
muni_data.loc[muni_data['autoSuff'].isin(['Autos<Workers']), 'autoSuff'] = 'Autos<Workers'
muni_data.loc[muni_data['autoSuff'].isin(['Autos>=Workers']), 'autoSuff'] = 'Autos>=Workers'
muni_data['autoSuff'] = muni_data['autoSuff'].astype('category')
muni_data['autoSuff'] = muni_data['autoSuff'].cat.set_categories(asuff_map.values())

#Boardings and trips by operator, tour purpose, access mode and auto-sufficiency
muni_collapsed = muni_data.groupby(['operator', 'tourPurpAgg', 'anchorAccessMode', 'autoSuff'])[['boardWeight','tripWeight']].sum().fillna(0)

'''
2013 VTA OBS data processing
Data processed by Joel Freedman - refer to Stata script "summarize scvta data.do" for details
'''
vta_data = pd.read_csv(r'data\3_SCVTA Data\VTA2013 Expanded.csv', low_memory=False)

#Updating columns to pd.category type
vta_data.loc[vta_data['tourPurpAgg'].isin(['Work']),'tourPurpAgg'] = '1_WORK'
vta_data.loc[vta_data['tourPurpAgg'].isin(['University']),'tourPurpAgg'] = '2_UNIVERSITY'
vta_data.loc[vta_data['tourPurpAgg'].isin(['School']),'tourPurpAgg'] = '3_SCHOOL'
vta_data.loc[vta_data['tourPurpAgg'].isin(['Maintenance']),'tourPurpAgg'] = '4_MAINTENANCE'
vta_data.loc[vta_data['tourPurpAgg'].isin(['Discretionary']),'tourPurpAgg'] = '5_DISCRETIONARY'
vta_data.loc[vta_data['tourPurpAgg'].isin(['At-work Subtour']),'tourPurpAgg'] = '6_AT-WORK SUBTOUR'
vta_data['tourPurpAgg'] = vta_data['tourPurpAgg'].astype('category')
vta_data['tourPurpAgg'] = vta_data['tourPurpAgg'].cat.set_categories(purpose_map.values())

vta_data.loc[vta_data['anchorAccessMode'].isin(['Walk']),'anchorAccessMode'] = '1_Walk'
vta_data.loc[vta_data['anchorAccessMode'].isin(['PNR']),'anchorAccessMode'] = '2_PNR'
vta_data.loc[vta_data['anchorAccessMode'].isin(['KNR']),'anchorAccessMode'] = '3_KNR'
vta_data['anchorAccessMode'] = vta_data['anchorAccessMode'].astype('category')
vta_data['anchorAccessMode'] = vta_data['anchorAccessMode'].cat.set_categories(access_mode_map.values())

vta_data.loc[vta_data['autoSuff'].isin(['0 Autos']), 'autoSuff'] = '0 Auto'
vta_data.loc[vta_data['autoSuff'].isin(['Autos<Workers']), 'autoSuff'] = 'Autos<Workers'
vta_data.loc[vta_data['autoSuff'].isin(['Autos>=Workers']), 'autoSuff'] = 'Autos>=Workers'
vta_data['autoSuff'] = vta_data['autoSuff'].astype('category')
vta_data['autoSuff'] = vta_data['autoSuff'].cat.set_categories(asuff_map.values())

#Boardings and trips by operator, tour purpose, access mode and auto-sufficiency
vta_collapsed = vta_data.groupby(['operator', 'tourPurpAgg', 'anchorAccessMode', 'autoSuff'])[['boardWeight','tripWeight']].sum().fillna(0)


'''
Finalizing transit trip targets 
1. Combine all collapsed boardings summaries
2. Compute expansion factor for each operator to scale down OBS to 2010 targets
3. Apply selected distributions of boardings by purpose and auto-sufficiency to operators that were not surveyed.
   The distributions are used from operators with similar characteristics (technology, ridership etc.)
   a. CR - Caltrain data
   b. EB - Data for all surveyed EB operators lumped together
   c. LB - LAVTA data
4. Collapse trips by technology, purpose, access mode and auto-sufficiency. This becomes the trip mode choice target
'''
#Combine all collapsed datasets
unified_collapsed = pd.concat([obs_collapsed, bart_collapsed, muni_collapsed, vta_collapsed])

#Calculate group total boardings by operator
obs_operator_totals = unified_collapsed['boardWeight'].groupby(level = 'operator').sum()

#Read in target boardings for 2010
boarding_targets = pd.read_csv(r'data\boardingTargets.csv')
target_operator_totals = boarding_targets.groupby('operator')['target_boardings'].sum()

#Expansion factors
expansion_factors = pd.concat([obs_operator_totals, target_operator_totals], axis = 1)
expansion_factors = expansion_factors.loc[expansion_factors['boardWeight'].notnull(),:]
expansion_factors['exp_factor'] = expansion_factors['target_boardings']/expansion_factors['boardWeight']
expansion_factors.index.name = 'operator' 
expansion_factors
'''
In [1]: expansion_factors
Out[1]: 
                               boardWeight  target_boardings  exp_factor
operator                                                                
AC Transit [EXPRESS]              15128.51             14704        0.97
AC Transit [LOCAL]               143442.42            160184        1.12
ACE                                4151.00              2025        0.49
BART                             352600.52            348991        0.99
Caltrain                          46384.69             37779        0.81
County Connection [EXPRESS]        1618.01              1322        0.82
County Connection [LOCAL]         10916.44              9302        0.85
Golden Gate Transit (ferry)        6795.00              6447        0.95
Golden Gate Transit [EXPRESS]     11986.00             11806        0.98
LAVTA                              5290.00              6093        1.15
Muni bus                         456361.15            514817        1.13
Muni cable car                    11490.63             27053        2.35
Muni metro                       120773.27            162023        1.34
Napa Vine [EXPRESS]                 150.60                83        0.55
Napa Vine [LOCAL]                  1653.55               628        0.38
Petaluma                           1063.66               673        0.63
SCVTA LRT                         42524.02             32156        0.76
SCVTA express bus                  5799.00              3316        0.57
SCVTA local bus                  122045.05             98118        0.80
SF Bay Ferry                       4589.76              4415        0.96
SamTrans [EXPRESS]                 1988.76              1481        0.74
SamTrans [LOCAL]                  42082.82             40823        0.97
Santa Rosa CityBus                10238.03              9986        0.98
Sonoma County                      4247.02              4459        1.05
Tri-Delta                          9849.20              8257        0.84
Union City                         2002.00              1696        0.85


NOTES
-----------
a. Ridership went down from 2010 for AC Transit [LOCAL], LAVTA, Sonoma County? Is this correct?

NTD Data comparison. The trend does seem to suggest that ridership decreased for LAVTA and AC Transit. For Sonoma County however, the ridership has slightly increased
The Sonoma County numbers do not jive. Since the ridership is low this can be ignored.
 	                    2008	        2009	      2010	        2011	      2012	        2013
LAVTA	           2,234,210 	   2,195,408     1,740,297 	   1,566,723     1,751,211 	   1,727,085 
SCVTA Bus	      33,388,223 	  34,778,402    32,210,839 	  31,652,434    32,338,378 	  32,745,967 
AC Transit	      65,194,287 	  60,468,401 	61,390,737 	  57,333,196 	53,642,880 	  55,234,888 
Sonoma County	   1,424,883 	   1,403,027 	 1,265,817 	   1,346,357 	 1,372,442 	   1,364,547 

b. No local Golden Gate Transit surveyed?
Marin Transit operates local Golden Gate Transit service and was not surveyed. Golden Gate Transit only operates express bus service.  
In TM2 transit network Marin Transit was included as Golden Gate Transit [LOCAL]. These boardings will be accounted for in "Other" category below
'''

#Apply expansion factors to scale survey data to year 2010
unified_collapsed = unified_collapsed.join(expansion_factors.loc[:,['exp_factor']], how='inner')
unified_collapsed['boardWeight_2010'] = unified_collapsed['boardWeight']*unified_collapsed['exp_factor']
unified_collapsed['tripWeight_2010'] = unified_collapsed['tripWeight']*unified_collapsed['exp_factor']

#Check [see if the final expanded boardings matches the targets]
check = pd.concat([unified_collapsed['boardWeight_2010'].groupby(level = 'operator').sum(), target_operator_totals], axis = 1)
check.loc[check['boardWeight_2010'].notnull(),:]
'''
In [3]: check = pd.concat([unified_collapsed['boardWeight_2010'].groupby(level = 'operator').sum(), target_operator_totals], axis = 1)
   ...: check.loc[check['boardWeight_2010'].notnull(),:]
Out[3]: 
                               boardWeight_2010  target_boardings
AC Transit [EXPRESS]                      14704             14704
AC Transit [LOCAL]                       160184            160184
ACE                                        2025              2025
BART                                     348991            348991
Caltrain                                  37779             37779
County Connection [EXPRESS]                1322              1322
County Connection [LOCAL]                  9302              9302
Golden Gate Transit (ferry)                6447              6447
Golden Gate Transit [EXPRESS]             11806             11806
LAVTA                                      6093              6093
Muni bus                                 514817            514817
Muni cable car                            27053             27053
Muni metro                               162023            162023
Napa Vine [EXPRESS]                          83                83
Napa Vine [LOCAL]                           628               628
Petaluma                                    673               673
SCVTA LRT                                 32156             32156
SCVTA express bus                          3316              3316
SCVTA local bus                           98118             98118
SF Bay Ferry                               4415              4415
SamTrans [EXPRESS]                         1481              1481
SamTrans [LOCAL]                          40823             40823
Santa Rosa CityBus                         9986              9986
Sonoma County                              4459              4459
Tri-Delta                                  8257              8257
Union City                                 1696              1696
'''

#Calculate distribution of trips/boardings by operator, tour purpose, access mode and auto sufficiency
obs_operator_trips = unified_collapsed['tripWeight_2010'].groupby(level = 'operator').sum()
obs_operator_brdngs = unified_collapsed['boardWeight_2010'].groupby(level = 'operator').sum()
unified_collapsed['shares_trips'] = unified_collapsed['tripWeight_2010'].div(obs_operator_trips, level = 0)
unified_collapsed['shares_brdngs'] = unified_collapsed['boardWeight_2010'].div(obs_operator_brdngs, level = 0)
unified_collapsed.to_csv(r'reports\unified_collapsed.csv')

#Calculate distribution of trips/boardings by technology, tour purpose, access mode and auto sufficiency
unified_collapsed_technology = unified_collapsed.reset_index()
unified_collapsed_technology = unified_collapsed_technology.merge(boarding_targets.loc[boarding_targets['surveyed'].isin([1]),['operator','technology']], left_on='operator', right_on='operator', how='left')
unified_collapsed_technology = unified_collapsed_technology.groupby(['technology','tourPurpAgg','anchorAccessMode','autoSuff'])['boardWeight','tripWeight','exp_factor','boardWeight_2010','tripWeight_2010'].sum()
unified_collapsed_technology['exp_factor'] = np.nan
obs_technology_trips = unified_collapsed_technology['tripWeight_2010'].groupby(level = 'technology').sum()
obs_technology_brdngs = unified_collapsed_technology['boardWeight_2010'].groupby(level = 'technology').sum()
unified_collapsed_technology['shares_trips'] = unified_collapsed_technology['tripWeight_2010'].div(obs_technology_trips, level = 0)
unified_collapsed_technology['shares_brdngs'] = unified_collapsed_technology['boardWeight_2010'].div(obs_technology_brdngs, level = 0)
unified_collapsed_technology.to_csv(r'reports\unified_collapsed_technology.csv')

#Remaining total boardings by technology to be distributed
other_operators = boarding_targets.loc[boarding_targets['surveyed'].isin([0]),:].groupby('technology')['target_boardings'].sum()
other_operators
'''
In [7]: other_operators
Out[7]: 
technology
CR             1754
EB             5751
LB            39477
Name: target_boardings, dtype: float64

Now we have to convert these trips to boardings and then distribute them across purpose, access mode and auto-sufficiency categories
'''

#Calculate transfer rates by operator
transfer_data = unified_collapsed[['boardWeight', 'tripWeight']].groupby(level = ['operator']).sum()
transfer_data['transfer_rate'] = transfer_data['boardWeight']/transfer_data['tripWeight']
transfer_data
'''
In [10]: transfer_data
Out[10]: 
                               boardWeight  tripWeight  transfer_rate
operator                                                             
AC Transit [EXPRESS]              15128.51    13098.29           1.15
AC Transit [LOCAL]               143442.42   107813.60           1.33
ACE                                4151.00     2904.49           1.43
BART                             352600.52   352600.52           1.00
Caltrain                          46384.69    38214.69           1.21
County Connection [EXPRESS]        1618.01     1048.91           1.54
County Connection [LOCAL]         10916.44     7210.81           1.51
Golden Gate Transit (ferry)        6795.00     6233.66           1.09
Golden Gate Transit [EXPRESS]     11986.00    10055.03           1.19
LAVTA                              5290.00     4022.95           1.31
Muni bus                         456361.15   384218.42           1.19
Muni cable car                    11490.63    11143.48           1.03
Muni metro                       120773.27   105591.77           1.14
Napa Vine [EXPRESS]                 150.60      127.52           1.18
Napa Vine [LOCAL]                  1653.55     1324.03           1.25
Petaluma                           1063.66      727.54           1.46
SCVTA LRT                         42524.02    32894.95           1.29
SCVTA express bus                  5799.00     4126.19           1.41
SCVTA local bus                  122045.05    85956.17           1.42
SF Bay Ferry                       4589.76     4135.14           1.11
SamTrans [EXPRESS]                 1988.76     1650.50           1.20
SamTrans [LOCAL]                  42082.82    32381.18           1.30
Santa Rosa CityBus                10238.03     7061.08           1.45
Sonoma County                      4247.02     3666.99           1.16
Tri-Delta                          9849.20     6869.41           1.43
Union City                         2002.00     1445.12           1.39
'''

#Calculate transfer rates by technology
transfer_data_technology = unified_collapsed_technology[['boardWeight', 'tripWeight']].groupby(level = ['technology']).sum()
transfer_data_technology['transfer_rate'] = transfer_data_technology['boardWeight']/transfer_data_technology['tripWeight']
transfer_data_technology
'''
In [35]: transfer_data_technology
Out[35]: 
            boardWeight  tripWeight  transfer_rate
technology                                        
CR             50535.69    41119.18           1.23
EB             36670.88    30106.44           1.22
Ferry          11384.76    10368.80           1.10
HR            352600.52   352600.52           1.00
LB            820681.96   653840.77           1.26
LR            163297.28   138486.72           1.18

BART system boardings are counted once per station entry. So a transfer between BART trains wont show up as a new unlinked BART trip. 
Therefore the unlinked trips are expanded directly to boardings. Hence HR transfer rate of 1.0
'''

#Other operator commuter rail targets [Caltrain transfer rates and distribution used]
CR_boardings = other_operators['CR']
CR_trips = CR_boardings/transfer_data.loc['Caltrain']['transfer_rate']
other_CR_distribution = unified_collapsed.loc['Caltrain'].reset_index()
other_CR_distribution['operator'] = 'Other_CR'
other_CR_distribution['boardWeight_2010'] = CR_boardings*other_CR_distribution['shares_brdngs']
other_CR_distribution['tripWeight_2010'] = CR_trips*other_CR_distribution['shares_trips']
other_CR_distribution['boardWeight'] = np.nan
other_CR_distribution['tripWeight'] = np.nan
other_CR_distribution['exp_factor'] = np.nan
other_CR_distribution = other_CR_distribution.set_index(['operator','tourPurpAgg','anchorAccessMode','autoSuff'])

#Other operator local bus targets [LAVTA transfer rates and distribution used]
#The average ridership of LB operators who were not surveyed is about 2500; LAVTA system is the closest surveyed in terms of ridership
#Sonoma County Transit maybe?? - CHECK
LB_boardings = other_operators['LB']
LB_trips = LB_boardings/transfer_data.loc['LAVTA']['transfer_rate']
other_LB_distribution = unified_collapsed.loc['LAVTA'].reset_index()
other_LB_distribution['operator'] = 'Other_LB'
other_LB_distribution['boardWeight_2010'] = LB_boardings*other_LB_distribution['shares_brdngs']
other_LB_distribution['tripWeight_2010'] = LB_trips*other_LB_distribution['shares_trips']
other_LB_distribution['boardWeight'] = np.nan
other_LB_distribution['tripWeight'] = np.nan
other_LB_distribution['exp_factor'] = np.nan
other_LB_distribution = other_LB_distribution.set_index(['operator','tourPurpAgg','anchorAccessMode','autoSuff'])

#Other operator express bus targets
#Average of all EB operators surveyed used
EB_boardings = other_operators['EB']
EB_trips = EB_boardings/transfer_data_technology.loc['EB']['transfer_rate']
other_EB_distribution = unified_collapsed_technology.loc['EB'].reset_index()
other_EB_distribution['operator'] = 'Other_EB'
other_EB_distribution['boardWeight_2010'] = EB_boardings*other_EB_distribution['shares_brdngs']
other_EB_distribution['tripWeight_2010'] = EB_trips*other_EB_distribution['shares_trips']
other_EB_distribution['boardWeight'] = np.nan
other_EB_distribution['tripWeight'] = np.nan
other_EB_distribution['exp_factor'] = np.nan
other_EB_distribution = other_EB_distribution.set_index(['operator','tourPurpAgg','anchorAccessMode','autoSuff'])

#Some housekeeping 
#By operator
all_collapsed_operators = pd.concat([unified_collapsed,other_LB_distribution,other_EB_distribution,other_CR_distribution])

#By technology
#Cable car is treated as Local 
all_collapsed_technology = all_collapsed_operators.reset_index()
all_collapsed_technology = all_collapsed_technology.merge(boarding_targets.loc[boarding_targets['surveyed'].isin([1]),['operator','technology']], left_on='operator', right_on='operator', how='left')
all_collapsed_technology.loc[all_collapsed_technology['operator'].isin(['Other_CR']),'technology'] = 'CR'
all_collapsed_technology.loc[all_collapsed_technology['operator'].isin(['Other_EB']),'technology'] = 'EB'
all_collapsed_technology.loc[all_collapsed_technology['operator'].isin(['Other_LB']),'technology'] = 'LB'
all_collapsed_technology = all_collapsed_technology.groupby(['technology','tourPurpAgg','anchorAccessMode','autoSuff'])['tripWeight_2010'].sum()

#Write out summaries
all_collapsed_operators.to_csv(r'reports\transit_trip_targets_operators.csv')
all_collapsed_technology.to_csv(r'reports\transit_trip_targets_technology.csv')
