import numpy as np
import matplotlib.pyplot as plt

def get_stats(data_list):
    my_stat_dict ={}
    my_stat_dict['mean'] = np.mean(data_list)
    my_stat_dict['std'] = np.std(data_list)
    my_stat_dict['max'] = np.max(data_list)
    my_stat_dict['min'] = np.min(data_list)
    return my_stat_dict
