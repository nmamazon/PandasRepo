import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

## seaborn plot
def sea_corr(dataframe, filename = None, title='', ltitle=''):
    c2 = dataframe.copy()
    c2.values[np.tril_indices_from(dataframe)] = np.nan
    cmean = c2.unstack().mean()
    print "%.2f" % cmean
    
    plt.figure(figsize=(11.7, 8.27))
    sns.set(style='white')
    
    # Generate Mask and cmap
    mask=np.zeros_like(dataframe)
    mask[np.triu_indices_from(mask)]= True
    #cmap = sns.diverging_palette(220,5,as_cmap=True)
    cmap = 'RdYlGn'
    
    # add subtitle
    plt.suptitle(title, fontsize=18)
    
    ax = sns.heatmap(dataframe, cmap=cmap, mask=mask, annot=True, linewidths=0.2, fmt='0.1f',
           vmin=-1, vmax=1,annot_kws={'size':8, 'alpha':0.6})
    plt.figtext(.5, .8, "Average Correlation = " + str('%.2f' % cmean) , bbox=dict(facecolor='white', pad=20))
    if filename != None:
        plt.savefig(filename, dpi=200, bbox_inches='tight')