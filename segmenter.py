import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.widgets import SpanSelector, RadioButtons
from pandas import DataFrame
from BColors.BColors import colors


class Segmenter(object):
    def __init__(self, data):
        self.fig = fig = plt.figure(figsize=(15, 15))
        self.classes = np.unique(data["class"])
        # Create axes
        data_names = [i for i in data if i != "class"]
        self.gs = gs = gridspec.GridSpec(len(data_names), 1)
        self.axes = axes = [fig.add_subplot(i) for i in gs]
        self.data = data
        self.plot()
        self.spans = [SpanSelector(axe, self.onselect, 'horizontal', useblit=True,
                                   rectprops=dict(alpha=0.5, facecolor='red')) for axe in axes]
        rax = plt.axes((.01,.1,.1,.03*len(self.classes)))
        self.radio = radio = RadioButtons(rax, self.classes)
        radio.on_clicked(self.clicked_radio)
        self.current_class_index = 0

    def clicked_radio(self, class_name):
        index = self.class_index(class_name)
        self.current_class_index = index
        print "Selected class %i" % index

    def class_name(self, class_index):
        return self.classes[class_index]

    def class_index(self, class_name):
        index = np.where(self.classes == class_name)[0][0]
        return index

    def plot(self):
        for axe in self.axes:
            axe.cla()
            axe.grid()
        for class_name, data in self.data.groupby("class"):
            del data["class"]
            class_index = self.class_index(class_name)
            x = data.index.values
            for axe, y, name in zip(self.axes, data.values.transpose(), data):
                axe.scatter(x, y, color=colors[class_index])
                axe.set_ylabel(name)
        self.gs.tight_layout(self.fig, rect=[0.1, 0.1, 1, 1])
        plt.tight_layout()

    def run(self):
        self.plot()
        plt.show()
        return self.data

    def onselect(self, xmin, xmax):
        self.data.loc[xmin:xmax]["class"] = self.class_name(self.current_class_index)
        self.plot()

if __name__ == '__main__':
    n_values = 1000
    n_classes = 4
    classes = np.array(["Class %i" % i for i in range(n_classes)])[np.linspace(0, n_classes-1, n_values).astype(int)]
    data = DataFrame(dict(A=np.arange(n_values), B=np.arange(n_values) * 0.5), index=np.linspace(0, 5, n_values))
    data["class"] = classes
    s = Segmenter(data)
    res = s.run()
    print(res)