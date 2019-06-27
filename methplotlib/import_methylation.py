import pandas as pd
import numpy as np
import sys


class Methylation(object):
    def __init__(self, table, data_type, name):
        self.table = table
        self.data_type = data_type
        self.name = name


def read_meth(filename, name, window, smoothen=5):
    """
    converts a file from nanopolish to a pandas dataframe
    input can be from calculate_methylation_frequency
    which will return a dataframe with 'chromosome', 'pos', 'methylated_frequency'
    smoothening the result by a rolling average

    input can also be raw data per read
    which will return a dataframe with 'read', 'chromosome', 'pos', 'log_lik_ratio', 'strand'
    """
    try:
        table = pd.read_csv(filename, sep="\t")
        table["pos"] = np.floor(table[['start', 'end']].mean(axis=1)).astype('i8')
        table = table.loc[(table["chromosome"] == window.chromosome)
                          & table["pos"].between(window.begin, window.end)]
        if 'log_lik_ratio' in table:  # indicating the file is 'raw'
            return Methylation(
                table=table.drop(columns=['start', 'end', 'log_lik_methylated',
                                          'log_lik_unmethylated', 'num_calling_strands',
                                          'num_motifs', 'sequence'])
                .sort_values(['read_name', 'pos']),
                data_type="raw",
                name=name)
        else:  # assuming the file is from calculate_methylation_frequency
            return Methylation(
                table=table.drop(columns=['start', 'end', 'num_motifs_in_group',
                                          'called_sites', 'called_sites_methylated',
                                          'group_sequence'])
                .sort_values('pos')
                .groupby('pos')
                .mean()
                .rolling(window=smoothen, center=True)
                .mean(),
                data_type="frequency",
                name=name)
    except Exception:
        sys.stderr.write("ERROR parsing {}\n\n\nDetailed error:\n".format(filename))
        raise


def get_data(methylation_files, names, window, smoothen=5):
    """
    Import methylation data from all files in the list methylation_files

    Data can be either frequency or raw.

    data is extracted within the window args.window
    Frequencies are smoothened using a sliding window
    """
    return [read_meth(f, n, window, smoothen) for f, n in zip(methylation_files, names)]
