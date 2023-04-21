"""
config.py
from los_analysis_modules import config

Configuration settings for LOS analysis program
"""

# Globals.  Use all caps.
# Boolean.  Is there data for ONE gel?  -> True.   If data for >1 gel, False.
# Another way to do this...
# List of tuples.  Each tuple = one pair of gels (proQ/coomassie)
# In program, loop through list -> analyze each tuple -> output results to separate excel tabs
# Number of gels could be a variable instead.  Then loop from 1 to # of gels

# Input file

# Output file

# Control strain ID
# Data will be relative to the average total of this strain, e.g. if MSA1, would use MSA1A, 1B, 1C...

# Normalization ID
# This should be the strain ID/label of the ONE strain that will be used to normalize across gels
# If there is only data for one gel, None.

# Sample strain dictionary...
# keys = sample_strain (e.g. MSA1A, MSA11, MSA39-1A); values = genotype



# functions
# return variables above

# verify that if "one gel" is True, Normalization ID is None.
# verify that if "one gel" is False, Normalization ID is NOT None.