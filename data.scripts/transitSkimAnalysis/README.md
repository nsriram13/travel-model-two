Instructions for running the transit skim analysis scripts
==============

Summary statistics
--------------

- Save the tpp files from transit skimming in a folders called skims_raw and skims - the "raw" version refers to the skim set before duplicate values are removed. Inspecting the raw version is optional. Comment out relevant parts if this needs to be disabled.
- Run transitSkimAnalysis.bat to export skims as csvs
- Run inspect_transit_skimset.py to summarize the skim data


Visualization
--------------

- In quickSkimRead.py ensure that infile points to the location where the skim csv files were written out
- PERIOD, TAP_BEING_QUERIED and TAP_NAME in the R script to generate a map of accessible taps