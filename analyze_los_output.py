"""
analyze_los_output.py

Take LOS gel raw data.  Normalize LOS data to protein levels, calculate
relative LOS levels vs. a control (e.g. WT), and format output for Prism.

Input should have:
- Sheet tabs named gel1_proq, gel1_coom, gel2_proq, gel2_coom, etc. for
Pro-Q Emerald and Coomassie stain data for each gel.
- Image name in cell A1
- Column headers in Excel row 2
- An inserted column called "Sample_strain" in ALL sheets containing a strain ID,
e.g. "MSA1A"
- An inserted column called "Carbohydrate" containing information about the type
of carbohydrate in that row (e.g. "Full", "Minimal", "RS15100_band")

python3 analyze_los_output.py <input.xlsx> <output.xlsx>

Sample command: python3 analyze_los_output.py 2023-03-30_rawdata.xlsx 2023-03-30_analyzed.xlsx
"""

import argparse
import pandas
import pandas as pd

# Globals to move to config eventually
INFILE_BASE = '2023-03-30_rawdata'
INFILE = INFILE_BASE + '.xlsx'
OUTFILE = INFILE_BASE + '_output.xlsx'
LOS_TYPES = ['Full', 'Intermediate', 'Minimal']
RS15100_ID = ['RS15100_band']  # Could change this to any other band to treat separately from LOS...  Have this as a list because I'll pass this to .isin(), like LOS_TYPES above.
CONTROL_ID = r'MSA1\D'  # 'MSA1\D' is regex; returns MSA1 followed by anything NOT a digit (i.e. not MSA11 or MSA13).  Eventually, make this into a config thing.  config.control + \D
STRAIN_ID_DICT = {
    "MSA1A": "17978 WT",
    "MSA1B": "17978 WT",
    "MSA1C": "17978 WT",
    "MSA39-1A": "\u0394pbpG",
    "MSA39-1B": "\u0394pbpG",
    "MSA39-2": "\u0394pbpG",
    "MSA9": "\u0394RS15100",
    "MSA11": "\u0394RS15100",
    "MSA13": "\u0394RS15100",
}


def combine_los_and_coomassie(proq_df: pd.DataFrame, coom_df: pd.DataFrame):
    """
    Merge coomassie and LOS data from separate dataframes

    proq_df: a pandas dataframe containing proQ data; must include a
    'Sample_strain' column containing strain IDs
    coom_df: a pandas dataframe containing coomassie data; must include a
    'Sample_strain' column containing strain IDs
    return: a left-merged dataframe
    """

    return pd.merge(proq_df, coom_df,
                    on='Sample_strain', how='left', suffixes=('proq', 'coom'))


def normalize_LOS_to_protein(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize LOS to protein levels in a merged pandas dataframe
    Returns data subset

    merged_df: a pandas dataframe containing merged LOS and coomassie data
    (i.e. returned from combine_los_and_coomassie)
    return: dataframe containing an extra column 'prot_norm_carb' with
    normalized protein-normalized carbohydrate data
    """

    merged_df['prot_norm_carb'] = \
        merged_df['Adj. Vol. (Int)proq'] / merged_df['Rel. Quant.coom']
    return merged_df


def calculate_control_mean(los_df: pd.DataFrame, ctrl_id: str) -> float:
    """
    Calculate mean of control values

    los_df: a data frame with a column 'Sample_strain' that contains strain
    IDs (one ID must be the ctrl_id parameter above), and another column
    'prot_norm_carb' containing protein-normalized carbohydrate data.
    Must contain ONLY LOS values, no RS15100/etc.
    return: the mean of control samples for normalization
    """

    # subset data to get only WT values
    wt_data = los_df[(los_df['Sample_strain'].str.contains(ctrl_id))]
    # groupby here will put the
    wt_totals = wt_data.groupby('Sample_strain').sum("prot_norm_carb")
    return sum(wt_totals['prot_norm_carb']) / len(wt_totals['prot_norm_carb'])


def calculate_relative_LOS(los_df: pd.DataFrame, wt_mean: float) -> pd.DataFrame:
    """
    For each row of carbohydrates, calculate its relative carbohydrate amount
    vs. the WT mean
    los_df: a dataframe containing LOS data; must have 'prot_norm_carb' column
    with protein-normalized levels of each LOS subtype
    wt_mean: a float; mean total WT LOS amount
    return: dataframe with a 'carb_rel_wt' column added containing carbohydrate
    amount relative to WT
    """

    pd.options.mode.chained_assignment = None  # avoid a warning that's irrelevant to what I'm doing
    los_df['carb_rel_wt'] = los_df['prot_norm_carb'] / wt_mean
    return los_df


def write_dfs_to_excel(dataframes, sheet_name, fpath):
    """ Write dfs to a single Excel sheet """
    with pd.ExcelWriter(fpath, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheet_name)
        writer.sheets[sheet_name] = worksheet

        column = 0
        row = 0

        for df in dataframes:
            df.name = df.index.item()
            worksheet.write_string(row, column, df.name)
            row += 1
            df.to_excel(writer, sheet_name=sheet_name,
                        startrow=row, startcol=column)
            row += df.shape[0] + 3


def log_processed_data(dataframe, fpath):
    """ Output full data, including calculations, to an excel sheet """

    with pd.ExcelWriter(fpath, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet('Processed data')
        writer.sheets['Processed data'] = worksheet

        dataframe.to_excel(writer, sheet_name='Processed data')


def main():
    """Business logic"""
    # args = get_cli_args()  # should get config file

    all_raw_data = pandas.read_excel(INFILE, sheet_name=None, header=1)
    # print(all_raw_data.keys())  # check names of raw data

    proq_1 = all_raw_data['gel1_proq']
    coom_1 = all_raw_data['gel1_coom']

    # TODO validate that relevant columns are present
    # TODO maybe validate lack of nans in relevant columns?

    # Normalize each proq sample to protein using coomassie[rel quant]
    merged_df = combine_los_and_coomassie(proq_df=proq_1, coom_df=coom_1)
    # Calculate protein-normalized carbohydrate data
    data = normalize_LOS_to_protein(merged_df=merged_df)

    # Subset for LOS data... must do this before calculating mean
    los_data = data[data['Carbohydrate'].isin(LOS_TYPES)]

    # Find average of total WT
    wt_mean = calculate_control_mean(los_df=los_data, ctrl_id=CONTROL_ID)

    # Get values relative to WT
    relative_LOS_df = calculate_relative_LOS(los_df=los_data, wt_mean=wt_mean)

    # Add genotype labels
    relative_LOS_df['Genotype'] = relative_LOS_df['Sample_strain'].map(STRAIN_ID_DICT)

    # Format data for prism
    data_to_output = relative_LOS_df[['Sample_strain', 'Genotype', 'Carbohydrate', 'carb_rel_wt']]

    # Get iterable of dataframes
    list_of_strain_data = []
    for strain in set(STRAIN_ID_DICT.values()):  # Iterate over unique strain genotypes
        strain_data = data_to_output[data_to_output['Genotype'] == strain]
        formatted_strain_data = strain_data.pivot(index='Genotype',
                                                  columns=['Sample_strain', 'Carbohydrate'],
                                                  values='carb_rel_wt')
        list_of_strain_data.append(formatted_strain_data)

    # Loop through list_of_strain_data and output to an Excel file
    write_dfs_to_excel(dataframes=list_of_strain_data,
                       sheet_name='LOS output',
                       fpath=OUTFILE)
    # TODO: either write partial header lines, OR write a function to delete some of it.

    # Store processed data in another tab of Excel file
    # TODO


    # TODO 151 analysis
    # rs15100_data = data[data['Carbohydrate'].isin(RS15100_ID)]


    # If two gels...
    # 1 make merged DFs
    # 2 for each gel, normalize_LOS_to_protein
    # 3 get LOS data
    # 4 Normalize each gel to the common-control strain (e.g. MSA1A)... may want to get total common-control amount and divide all #s by that one
    # 5 merge the two gels
    # 6 calculate_control_mean on combined dataset
    # 7 calculate_relative_LOS
    # 8 format and print


# TODO: supply config file to argparse.  That should deal with input, output, etc.
# def get_cli_args():
#     """
#     void: get_cli_args()
#     Takes: no arugments
#     Returns: instance of argparse arguments
#     """
#
#     parser = argparse.ArgumentParser(description=__doc__)
#
#     parser.add_argument("--input", default="-", metavar="INPUT_FILE", type=argparse.FileType("r"),
#                         help="path to .xlsx containing data", required=True)
#
#     parser.add_argument("--output", default="-", metavar="OUTPUT_FILE", type=argparse.FileType("w"),
#                         help="path to the output file", required=True)
#
#     return parser.parse_args()


if __name__ == "__main__":
    main()
