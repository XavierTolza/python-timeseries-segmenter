import numpy as np


def segment_dataframe_per_column(df, column):
    array = df[column].values
    stops = np.where(array[1:] != array[:-1])[0] + 1
    starts = np.concatenate([[0], stops])
    stops = np.concatenate([stops, [len(array)]])

    for start, stop in zip(starts, stops):
        yield array[start], df.iloc[start:stop]