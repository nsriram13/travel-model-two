"""
Script for snapping the arterial count locations to nearby links on the all streets network.
Counts data has x,y coordinates and the name of the street they are on. All streets network is a shapefile with street names. 

@author: sn (02/20/2015)
"""

import os
import re
import numpy as np
import pandas as pd
from osgeo import ogr, gdalconst
import rtree
from fuzzywuzzy import fuzz
from time import strftime
pd.set_option('display.width',300)

#Set file names
count_locations = r'inputs\gis\geocommons_count_project.shp'
all_streets_network = r'inputs\gis\tana_links.shp'
all_streets_data = r'inputs\tana_links.csv'
arterial_counts = r'inputs\2011_MTC_TrafficData_GEOCOMMONS.csv'

#Settings
_start_distance = 100.0
_max_distance = 1000.00
logFile = r'eventLog.txt'

#TODO: Clean this up and work this into the code logic.
check_stations = set([14,70,78,192,203,219,261,275,314,340,390,398,401,407,410,416,422,423,534,573,617,666,733,756,780,786,787,827,848,863,963,966,983,992,1056,1075,1155,1252,1290,1296,1316])


'''
-------------------------------------------------------------------------------------------------------
Function Definitions
-------------------------------------------------------------------------------------------------------
'''
def standardizeStreetNames(street):
    '''
    Function to perform multiple string replacements
    Finds and replaces all occurences of patterns in `street` as defined by the mapping in dictionary `d`
    '''
    
    #Dictionary of street name modification; these are some of the common name mismatches that were identified
    d={'east':'e'
        ,'west':'w'
        ,'tewlfth':'12th'
        ,'eleventh':'11th'
        ,'tenth':'10th'
        ,'ninth':'9th'
        ,'eighth':'8th'
        ,'seventh':'7th'
        ,'sixth':'6th'
        ,'fifth':'5th'
        ,'fourth':'4th'
        ,'third':'3rd'
        ,'second':'2nd'
        ,'first':'1st'
        ,'street':'st'
        ,'wy': 'way'
       }

    pattern = re.compile(r'\b(' + '|'.join(sorted(d.keys(), key=len, reverse=True)) + r')\b')
    standard_street = pattern.sub(lambda x: d[x.group()], street)
    return(standard_street)

def broadcast_nth_elem(g, n=0):
    '''Broadcast the nth value into the rest of Series. Use with transform to do grouped operation'''
    return g.iloc[n]

'''
-------------------------------------------------------------------------------------------------------
Main Program Area
-------------------------------------------------------------------------------------------------------
'''
#Read in spatial datasets
all_streets = ogr.Open(all_streets_network, gdalconst.GA_ReadOnly)
all_streets_layer = all_streets.GetLayer()

count_stations = ogr.Open(count_locations, gdalconst.GA_ReadOnly)
count_stations_layer = count_stations.GetLayer()

'''
Create an R-tree index for all-streets network for performing quick spatial queries

NOTE
-------
All features, once read, are cached in memory as a dictionary. It can be queried like so: link_id, link_name, link_feature, link_geometry = features[FID].
However, if memory is an issue, do disk reads this way link_feature = layer.GetFeature(FID) and so on. No caching is required but slower.
'''
features = {}
index = rtree.index.Index(interleaved=False)
for FID in range(0, all_streets_layer.GetFeatureCount()):
    link_feature = all_streets_layer.GetFeature(FID)
    link_geometry = link_feature.GetGeometryRef()
    link_id = (link_feature.GetField('A'),link_feature.GetField('B'))
    link_name = link_feature.GetField('NAME')
    xmin, xmax, ymin, ymax = link_geometry.GetEnvelope()
    index.insert(FID, (xmin, xmax, ymin, ymax))
    features[FID] = (link_id, link_name, link_feature, link_geometry,)

logger = open(logFile, "wb")
all_matches = pd.DataFrame(columns=['FID','COUNT_LOCATION','LINK_FID','A','B','LINK_NAME','DISTANCE'])

'''
Create a search envelope of `distance` ft around the count locations and get the set of nearby streets.
R-tree is used to perform quick nearest neighbor search. See here for more information on Python implementation 
of R-tree: http://toblerity.org/rtree/
'''
for FID1 in range(0, count_stations_layer.GetFeatureCount()):

    #Initiate the search with just the minimum distance
    distance = _start_distance

    #Get feature and geometry of the count station
    station = count_stations_layer.GetFeature(int(FID1))
    point_geometry = station.GetGeometryRef()
    street_name = station.GetField('On_Loc')

    if int(FID1) in check_stations:
        distance += 100.0

    #Determine the bounding box and expand by `distance` ft to search
    xmin, xmax, ymin, ymax = point_geometry.GetEnvelope()
    search_space = (xmin-distance, xmax+distance, ymin-distance, ymax+distance)

    #Find all links within the specified distance
    nearby_links = list(index.intersection(search_space))
    num_matches = len(nearby_links)

    #Expand the search space until atleast 2 link are found; Search is stopped after `_max_distance` ft.
    while num_matches < 2:
        distance += 50.0

        if distance < _max_distance:
            search_space = (xmin-distance, xmax+distance, ymin-distance, ymax+distance)
            nearby_links = list(index.intersection(search_space))
            num_matches = len(nearby_links)
            logger.write('Search space expanded for {}'.format(int(FID1)) + os.linesep)
        else:
            num_matches = 3
            logger.write('No match found for Station {} within a 1000 ft search radius'.format(int(FID1)) + os.linesep)

    '''
    R-Tree uses minimum bounding boxes to find the nearest features. The actual distance needs to be computed using gdal Distance method
    It is possible that the actual distance to all returned links is more than the threshold. This results in an empty set.
    Relaxing the distance to maximum actual distance of all returned links just for those cases
    '''
    if nearby_links:
        #Calculate actual feature separation
        link_geometries = [features[fid][3] for fid in nearby_links]
        feature_spearation = [point_geometry.Distance(link) for link in link_geometries]
        
        if ([separation<distance for separation in feature_spearation].count(True) < 2):
            logger.write('Distance calculation relaxed for Station {}'.format(int(FID1)) + os.linesep)
            distance = max(feature_spearation)
    
    i=1
    '''Save the match details into a DataFrame'''
    for FID2 in nearby_links:
        link_id, link_name, link_feature, link_geometry = features[FID2]
        feature_separation = point_geometry.Distance(link_geometry)
        if (feature_separation <= distance):
            logger.write('{} Street: {} is near {} Street:{}'.format(int(FID1), street_name, link_id,link_name) + os.linesep)
            all_matches.loc[(int(FID1),i),:]=array([int(FID1), street_name, int(FID2), link_id[0],link_id[1],link_name,feature_separation], dtype=object)
            i=i+1
logger.close()

'''
For each nearest street we perform some basic cleansing. Compute a string matching fuzzy score and see 
which streets comes out on top (sort by direct string match, distance and then the different scores)
Convert all street names to lower case and then do string replacements for some common patterns
fuzzywuzzy is used to score string similarity
See here for more information on FuzzyWuzzy http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/
'''
all_matches['COUNT_LOCATION'] = all_matches['COUNT_LOCATION'].str.lower().apply(standardizeStreetNames)
all_matches.loc[all_matches['LINK_NAME'].isnull(),'LINK_NAME'] = ''     #some of the street names were NaN. Comverting to empty string
all_matches['LINK_NAME'] = all_matches['LINK_NAME'].str.lower().apply(standardizeStreetNames)
all_matches['DIRECT_STRING_SIMILARITY_INDEX'] = all_matches.loc[~all_matches['LINK_NAME'].isnull(),['COUNT_LOCATION','LINK_NAME']].apply(lambda x: fuzz.ratio(x['COUNT_LOCATION'], x['LINK_NAME']), axis=1)
all_matches['PARTIAL_STRING_SIMILARITY_INDEX'] = all_matches.loc[~all_matches['LINK_NAME'].isnull(),['COUNT_LOCATION','LINK_NAME']].apply(lambda x: fuzz.partial_ratio(x['COUNT_LOCATION'], x['LINK_NAME']), axis=1)
all_matches['TOKEN_SORT_SCORE'] = all_matches.loc[~all_matches['LINK_NAME'].isnull(),['COUNT_LOCATION','LINK_NAME']].apply(lambda x: fuzz.token_sort_ratio(x['COUNT_LOCATION'], x['LINK_NAME']), axis=1)
all_matches['TOKEN_SET_SCORE'] = all_matches.loc[~all_matches['LINK_NAME'].isnull(),['COUNT_LOCATION','LINK_NAME']].apply(lambda x: fuzz.token_set_ratio(x['COUNT_LOCATION'], x['LINK_NAME']), axis=1)


'''Sort the result'''
all_matches = all_matches.sort_index(by=['FID','DIRECT_STRING_SIMILARITY_INDEX', 'DISTANCE','PARTIAL_STRING_SIMILARITY_INDEX','TOKEN_SORT_SCORE','TOKEN_SET_SCORE'], ascending=[True,False,True,False,False,False])


'''
Check for erroneous matches

CASE 1
-----------
If two links are right on top of each other then their nodes would be reversed i.e. A-B = B-A. 
The node-set has a cardinality is 2. Counts will map to two links and they will have the same 
distance from the point. This is also the case when counts map to only one link. In both cases
it is highly likely that the match is correct.

CASE 2
-----------
If one of the links is the extension of the other link they will share a node A-B,B-C. The node-set 
has a cardinality is 3. This is also true of when count location is near a cross-street.
These are faulty cases and needs to be removed.

CASE 3
-----------
If it is a two-way street and the links are physically spearate then they will share no nodes node 
A-B,C-D. The node-set has a cardinality is 4. We can ensure a correct match by checking the street
name.
'''

all_matches_grouped = all_matches.groupby('FID')
all_matches['A_TEMP'] = all_matches_grouped['A'].transform(broadcast_nth_elem)
all_matches['B_TEMP'] = all_matches_grouped['B'].transform(broadcast_nth_elem)
all_matches['CHECK'] = all_matches[['A','B','A_TEMP','B_TEMP']].apply(lambda x: len(set(x)),axis=1)
all_matches = all_matches.loc[all_matches['CHECK']!=3,:]

#Write out csv file for inspection
report = all_matches.groupby('FID').head(2)
all_matches.to_csv('all_matches.csv')
report.to_csv('report.csv')
