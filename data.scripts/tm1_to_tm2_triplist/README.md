Instructions
==============

About
--------------
Script to convert Travel Model One (TM1) trip lists into synthetic Travel Model Two (TM2) trip lists.
Each TAZ in the TM1 has the MAZs contained within (centroid based) as alternatives.
A size-term-based probability array is computed and a Monte Carlo selection of TM2 MAZ is performed. 

The user has to specify the following parameters
--------------
@param sizeCoefficientsFile: csv file that holds the size coefficients (borrowed from TM1 model)
@param mazDataFile: TM2 MAZ data file
@param MAZ_to_TM1TAZ_xwalk: TM2 MAZ to TM1 TAZ
@param householdsFile: Household data from TM1 100% run
@param geographicCWalkFile: Crosswalk between different TM2 geographies
@param inputTripFile: Trip list from TM1 100% run
@param outputTripFile: File name of output trip list
@param jointFlag: [True/False] Logical variable indicating whether the trip list being processed is joint or individual

meta
--------------
@date: 2014-04-14
@author: sn, narayanamoorthys AT pbworld DOT com