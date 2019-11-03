import numpy as np
import pandas as pd

small_df = pd.DataFrame(np.random.rand(4,4),index=list('2346'),columns=list('ABCD'))

small_df.iloc[3][0] = 'Scraped'

big_df = pd.DataFrame(np.zeros((9,4)),index=list('123456789'),columns=list('ABCD'))

big_df['A'] = small_df['A'].combine_first(big_df['A'])