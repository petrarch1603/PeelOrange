import numpy as np
import matplotlib.pyplot as plt


class StatAnalysis:
    def __init__(self, lyr):
        self.field_name = 'scale_dist'
        self.lyr = lyr
        self.data_list = self.get_data_list()
        self.stats_dict = self.get_stats_dict()

    def get_data_list(self):
        my_data_points = []
        field_index = self.lyr.fields().indexFromName(self.field_name)
        for i in self.lyr.getFeatures():
            my_data_points.append(i.attributes()[field_index])
        return my_data_points

    def get_stats_dict(self):
        return {'mean': np.mean(self.data_list),
                'std': np.std(self.data_list),
                'max': np.max(self.data_list),
                'min': np.min(self.data_list)}

