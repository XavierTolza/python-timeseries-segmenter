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

        self.axe_zoom = axe_zoom = plt.axes((.15,.03,.84,.05))
        self.span_zoom = SpanSelector(axe_zoom, self.select_zoom, 'horizontal', useblit=True,
                                      rectprops=dict(alpha=0.5, facecolor='green'))
        self.spans = [SpanSelector(axe, self.onselect, 'horizontal', useblit=True,
                                   rectprops=dict(alpha=0.5, facecolor='red')) for axe in axes]
        rax = plt.axes((0.005,.1,.1,.03*len(self.classes)))
        self.radio = radio = RadioButtons(rax, self.classes)
        radio.on_clicked(self.clicked_radio)
        self.current_class_index = 0
        self.zoom = np.array([np.min(data.index.values), np.max(data.index.values)])
        self.zoom_ylim = None
        self.zoom_fill = None
        self.plot()

    def clicked_radio(self, class_name):
        index = self.class_index(class_name)
        self.current_class_index = index
        print "Selected class %i" % index

    def class_name(self, class_index):
        return self.classes[class_index]

    def class_index(self, class_name):
        index = np.where(self.classes == class_name)[0][0]
        return index

    def select_zoom(self, min, max):
        data = [min, max]
        self.zoom = np.array([np.min(data),np.max(data)])
        self.plot()

    @property
    def data_filtered(self):
        return self.data[[i for i in data if i != "class"]]

    def plot(self):
        zoom = self.zoom
        zoom_margin = np.abs(zoom[1]-zoom[0])*0.01
        zoom = zoom + zoom_margin * np.array([-1, 1])

        for axe in self.axes:
            axe.cla()
            axe.grid()
        for class_name, data in self.data.groupby("class"):
            del data["class"]
            class_index = self.class_index(class_name)
            x = data.index.values
            selector = np.logical_and(x > zoom[0], x < zoom[1])
            for axe, y, name in zip(self.axes, data.values.transpose(), data):
                axe.scatter(x[selector], y[selector], color=colors[class_index])
                axe.set_ylabel(name)

        axe_zoom = self.axe_zoom
        if self.zoom_ylim:
            ylim = self.zoom_ylim
            self.zoom_fill.remove()
        else:
            data = self.data_filtered
            x = data.index.values
            for i, (d, name) in enumerate(zip(self.data.values.transpose(), data)):
                axe_zoom.plot(x, d, label=name, color=colors[i], zorder=i+10)
            axe_zoom.set_xlim(x.min(), x.max())
            ylim = axe_zoom.get_ylim()
            self.zoom_ylim = ylim
        self.zoom_fill = axe_zoom.fill_between(zoom, [ylim[0]]*2, [ylim[1]]*2, color="green", alpha=".1", zorder=0)
        self.gs.tight_layout(self.fig, rect=[0.1, 0.1, 1, 1])

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
    columns = "A,B,C,D".split(",")
    data = np.cumsum(np.random.normal(0, .1, (n_values, len(columns))), 0)
    data = DataFrame(data,
                     index=np.linspace(0, 5, n_values), columns=columns)
    data["class"] = classes
    s = Segmenter(data)
    res = s.run()
    print(res)