import matplotlib.pyplot as plt
import numpy as np
from BColors.BColors import colors
from matplotlib import gridspec
import matplotlib.patches as mpatches
from matplotlib.widgets import SpanSelector, RadioButtons


class Segmenter(object):
    class PlotMethod(object):
        SCATTER = 0
        PLOT = 1
    def __init__(self, data, plot_method=PlotMethod.SCATTER, **kwargs):
        self.fig = fig = plt.figure(figsize=(15, 15))
        self.classes = np.unique(data["class"])
        # Create axes
        data_names = [i for i in data if i != "class"]
        self.gs = gs = gridspec.GridSpec(len(data_names), 1)
        self.axes = axes = [fig.add_subplot(i) for i in gs]
        self.data = data

        self.axe_zoom = axe_zoom = plt.axes((.15, .03, .84, .05))
        self.span_zoom = SpanSelector(axe_zoom, self.select_zoom, 'horizontal', useblit=True,
                                      rectprops=dict(alpha=0.5, facecolor='green'))
        self.spans = [SpanSelector(axe, self.onselect, 'horizontal', useblit=True,
                                   rectprops=dict(alpha=0.5, facecolor='red')) for axe in axes]
        self.radio_axe = rax = plt.axes((0.005, .1, .1, .03 * len(self.classes)))
        self.radio = radio = RadioButtons(rax, self.classes)
        radio.on_clicked(self.clicked_radio)
        self.current_class_index = 0
        self.zoom = np.array([np.min(data.index.values), np.max(data.index.values)])
        self.zoom_ylim = None
        self.zoom_xlim = None
        self.zoom_fill = None
        self.plot_method = plot_method
        self.kwargs = kwargs
        self.plot()
        self.__create_legend()

    def clicked_radio(self, class_name):
        index = self.class_index(class_name)
        self.current_class_index = index
        print "Selected class %i" % index

    def class_name(self, class_index):
        return self.classes[class_index]

    def class_index(self, class_name):
        index = np.where(self.classes == class_name)[0][0]
        return index

    def select_zoom(self, start, stop):
        data = [start, stop]
        self.zoom = np.array([np.min(data), np.max(data)])
        self.plot()

    @property
    def data_filtered(self):
        return self.data[[i for i in self.data if i != "class"]]

    def __create_legend(self):
        patches = []
        for class_index, class_name in enumerate(self.classes):
            patches.append(mpatches.Patch(color=colors[class_index], label=class_name))
        n_classes = len(self.classes)
        self.radio_axe.legend(handles=patches, loc=3, mode="expand",
                              bbox_to_anchor=(0., 1.02, 1., .102 * n_classes))

    def plot(self):
        zoom = self.zoom
        zoom_margin = np.abs(zoom[1] - zoom[0]) * 0.01
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
                kwargs = dict(color=colors[class_index])
                kwargs.update(self.kwargs)
                if self.plot_method == self.PlotMethod.SCATTER:
                    axe.scatter(x[selector], y[selector], **kwargs)
                elif self.plot_method == self.PlotMethod.PLOT:
                    axe.plot(x[selector], y[selector], **kwargs)
                else:
                    raise ValueError("Incorrect plot method: %i" % self.plot_method)
                axe.set_ylabel(name)

        axe_zoom = self.axe_zoom
        if self.zoom_ylim:
            ylim = self.zoom_ylim
            xlim = self.zoom_xlim
            self.zoom_fill.remove()
        else:
            data = self.data_filtered
            x = data.index.values
            for i, (d, name) in enumerate(zip(self.data.values.transpose(), data)):
                axe_zoom.plot(x, d, label=name, color=colors[i], zorder=i + 10)
            # axe_zoom.set_xlim(x.min(), x.max())
            self.zoom_ylim = ylim = axe_zoom.get_ylim()
            self.zoom_xlim = xlim = axe_zoom.get_xlim()
        self.zoom_fill = axe_zoom.fill_between(zoom, [ylim[0]] * 2, [ylim[1]] * 2, color="green", alpha=".1", zorder=0)
        axe_zoom.set_xlim(xlim)
        self.gs.tight_layout(self.fig, rect=[0.1, 0.1, 1, 1])

    def run(self):
        self.plot()
        plt.show()
        return self.data

    def onselect(self, xmin, xmax):
        self.data.loc[xmin:xmax]["class"] = self.class_name(self.current_class_index)
        self.plot()
