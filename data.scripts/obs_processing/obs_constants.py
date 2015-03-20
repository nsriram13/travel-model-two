import numpy as np

#Worker codes crosswalk
worker_crosswalk = { 'zero':0
,'one':1
,'two':2
,'three':3
,'four':4
,'five':5
,'six':6
,'six or more':6
,'seven':7
,'eight':8
,'nine':9
,'ten':10
,'eleven':11
,'twelve':12
,'thirteen':13
,'fourteen':14
,'fifteen':15
,'other': np.nan
}

#Vehicle codes crosswalk
vehicles_crosswalk={'zero':0
,'one':1
,'two':2
,'three':3
,'four':4
,'four or more':4
,'five':5
,'six':6
,'seven':7
,'eight':8
,'nine':9
,'ten':10
,'twelve':12
,'other': np.nan
}

#Number of person codes crosswalk
persons_crosswalk = {'one':1
,'two':2
,'three':3
,'four':4
,'five':5
,'six':6
,'seven':7
,'eight':8
,'nine':9
,'ten or more':10
}

#Aggregate tour purpose crosswalk and purpose heirarchy
tour_purp_crosswalk = {'work':'1_WORK'
,'work-related':'1_WORK'
,'university':'2_UNIVERSITY'
,'college':'2_UNIVERSITY'
,'school':'3_SCHOOL'
,'grade school':'3_SCHOOL'
,'high school':'3_SCHOOL'
,'escorting':'4_MAINTENANCE'
,'shopping':'4_MAINTENANCE'
,'other maintenance':'4_MAINTENANCE'
,'social recreation':'5_DISCRETIONARY'
,'eat out':'5_DISCRETIONARY'
,'other discretionary':'5_DISCRETIONARY'
,'at work':'6_AT-WORK SUBTOUR'
}

purpose_map = {1:'1_WORK',
               2:'2_UNIVERSITY',
               3:'3_SCHOOL',
               4:'4_MAINTENANCE',
               5:'5_DISCRETIONARY',
               6:'6_AT-WORK SUBTOUR'}

#Anchor access mode heirarchy
access_mode_map = {1:'1_Walk',
                   2:'2_PNR',
                   3:'3_KNR'}

#Auto sufficiency heirarchy
asuff_map = {1:'0 Auto',
                   2:'Autos<Workers',
                   3:'Autos>=Workers'}



#List of operators surveyed and their standardized names
surveyed_operators = {'AC Transit': 'AC TRANSIT'
,'ACE':'ACE'
,'Caltrain':'CALTRAIN'
,'County Connection':'COUNTY CONNECTION'
,'Golden Gate Transit (bus)':'GOLDEN GATE TRANSIT'
,'Golden Gate Transit (ferry)':'GOLDEN GATE FERRY'
,'LAVTA':'WHEELS (LAVTA)'
,'Napa Vine':'NAPA VINE'
,'Petaluma':'PETALUMA TRANSIT'
,'SF Bay Ferry':'SF BAY FERRY'
,'SamTrans':'SAMTRANS'
,'Santa Rosa CityBus':'SANTA ROSA CITYBUS'
,'Sonoma County':'SONOMA COUNTY TRANSIT'
,'Tri-Delta':'TRI-DELTA'
,'Union City':'UNION CITY'}

#All operators appearing in the dataset and their standardized names
all_operators = {'AC TRANSIT':'AC TRANSIT'
,'ACE':'ACE'
,'AMTRAK':'AMTRAK'
,'BART':'BART'
,'BLUE & GOLD FERRY':'BLUE & GOLD FERRY'
,'CALTRAIN':'CALTRAIN'
,'COUNTY CONNECTION':'COUNTY CONNECTION'
,'DUMBARTON EXPRESS':'DUMBARTON EXPRESS'
,'EMERY-GO-ROUND':'EMERY-GO-ROUND'
,'FAIRFIELD-SUISUN':'FAIRFIELD-SUISUN'
,'GOLDEN GATE FERRY':'GOLDEN GATE FERRY'
,'GOLDEN GATE TRANSIT':'GOLDEN GATE TRANSIT'
,'MARIN TRANSIT':'MARIN TRANSIT'
,'MODESTO TRANSIT':'MODESTO TRANSIT'
,'MUNI':'MUNI'
,'NAPA VINE':'NAPA VINE'
,'OTHER':'OTHER'
,'PETALUMA TRANSIT':'PETALUMA TRANSIT'
,'PRIVATE SHUTTLE':'PRIVATE SHUTTLE'
,'SAMTRANS':'SAMTRANS'
,'SAN JOAQUIN TRANSIT':'SAN JOAQUIN TRANSIT'
,'SANTA ROSA CITY BUS':'SANTA ROSA CITYBUS'
,'SANTA ROSA CITYBUS':'SANTA ROSA CITYBUS'
,'SF BAY FERRY':'SF BAY FERRY'
,'SOLTRANS':'SOLTRANS'
,'SONOMA COUNTY TRANSIT':'SONOMA COUNTY TRANSIT'
,'STANFORD SHUTTLES':'STANFORD SHUTTLES'
,'TRI-DELTA':'TRI-DELTA'
,'UNION CITY':'UNION CITY'
,'VALLEJO TRANSIT':'VALLEJO TRANSIT'
,'VTA':'VTA'
,'WESTCAT':'WESTCAT'
,'WHEELS (LAVTA)':'WHEELS (LAVTA)'}

