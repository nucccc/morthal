'''
here it would be nice if I was to just think about some stupid plots from the dataframe
'''

import polars as pl
import seaborn as sns
from matplotlib import pyplot as plt

def gen_plots(funcs_df: pl.DataFrame):
    

    sns.displot(funcs_df.to_pandas(), x = 'n_nodes', kind='kde')
    plt.savefig('n_nodes_dist.png')

    sns.displot(funcs_df.to_pandas(), x = 'n_exprs', kind='kde')
    plt.savefig('n_exprs_dist.png')
