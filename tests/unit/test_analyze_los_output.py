"""
test suite for analyze_los_output.py
"""
import plistlib

import pandas as pd
#from analyze_los_output import combine_los_and_coomassie

# Globals
# data to make into coomassie and proq dfs
TEST_PROQ_DATA = {'Sample_strain': 'test1',
                  'Adj. Vol. (Int)': [10],
                  }
TEST_COOM_DATA = {'Sample_strain': 'test1',
                  'Rel. Quant.': [5],
                  }
# data to make into a dummy merged df
TEST_MERGED_DATA = {'Sample_strain': 'test1',
                    'Rel. Quant.': [5],
                    'Adj. Vol. (Int)': [10],
                  }

# helper functions?
# might need to have a sort df type function... not sure
# def test_combine_los_and_coomassie():
#     """ Verify that function merges datasets correctly """
#     test_proq = pd.DataFrame.from_dict(TEST_PROQ_DATA)
#     test_coom = pd.DataFrame.from_dict(TEST_COOM_DATA)
#     assert combine_los_and_coomassie(test_proq, test_coom) == pd.DataFrame.from_dict(TEST_MERGED_DATA), 'failed to merge data'
test_proq = pd.DataFrame.from_dict(TEST_PROQ_DATA)
test_coom = pd.DataFrame.from_dict(TEST_COOM_DATA)
print(pd.merge(test_proq, test_coom, on='Sample_strain', how='left', suffixes=('proq', 'coom')))


#pd.merge(proq_df, coom_df,
#                    on='Sample_strain', how='left', suffixes=('proq', 'coom'))



# test_normalize_LOS_to_protein()
# make merged df
# assert that the normalized column has predicted values?

# test_calculate_control_mean()
# assert it's equal to expected value...

# test_calculate_relative_LOS()
# assert column contains expected value.

