'''
author: sn (2014-10-24)
Script to compute eucledian distance matrix for large number of points using the high performance scipy spatial library
Refer: http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist

THIS IMPLEMNTATION COMPUTES TAP to TAP distance for MTC transit network
'''
import os,sys
import pandas as pd
import numpy as np
import scipy.spatial.distance as spdist

#Setting up file paths
temp_path = os.path.dirname(sys.argv[0])
model_run_dir = os.path.abspath(temp_path)
NODE_CSV_FILE = model_run_dir + r'\tap_tap_distance\mtc_final_network_with_tolls.csv'

#Read in network node data and fetch TAP node set
NODE_DATA = pd.read_csv(NODE_CSV_FILE, low_memory=False)
#TAP_NODE_DATA = NODE_DATA.loc[NODE_DATA['TAPSEQ'] > 0].set_index(['TAPSEQ']).loc[:,['X','Y']].sort()
MAZ_NODE_DATA = NODE_DATA.loc[NODE_DATA['MAZSEQ'] > 0].set_index(['MAZSEQ']).loc[:,['X','Y']].sort()

#Compute euclidean distance in 2 dimensional space
tap_dist = spdist.squareform(spdist.pdist(TAP_NODE_DATA.as_matrix(), 'euclidean'))
maz_dist = spdist.squareform(spdist.pdist(MAZ_NODE_DATA.as_matrix(), 'euclidean'))

tap_dist = tap_dist/5280 #Converting feet to miles
maz_dist = maz_dist/5280 #Converting feet to miles
#np.savetxt('model_run_dir + r'\tap_tap_distance\tap_dist.csv', tap_dist, delimiter=",")
