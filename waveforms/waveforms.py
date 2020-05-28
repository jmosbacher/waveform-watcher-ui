
import panel as pn
import holoviews as hv
import param
import numpy as np
import pandas as pd
import datetime as dt
import strax
# import straxen
pn.extension()
hv.extension("bokeh")


peaks = np.load("181028_0045_peaks.npy")
events = pd.read_pickle("181028_0045_event_info.pkl")
dset = hv.Dataset(events)


class WaveformWatcher(param.Parameterized):
    DIMS = [
    ["cs1", "cs2"],
    ["z","r" ],
    ["e_light", 'e_charge'],
    ["e_light", 'e_ces'],
    ["drift_time", "n_peaks"],
    ]

    dates = param.DateRange(default=(dt.datetime(2016, 11, 10),dt.datetime.utcnow()), bounds=(dt.datetime(2016, 11, 10), dt.datetime.utcnow()))
    runs = param.List(default=[])
    sources = param.List(default=[],)
    linked_selection = param.Parameter()
    selection_spaces = param.List(default=DIMS)
    events = param.DataFrame(default=pd.DataFrame())

    def __init__(self, **params):
        super().__init__(**params)
        self.linked_selection = hv.selection.link_selections.instance()

    @param.depends("selection_spaces", watch=True)
    def event_selection(self):
        if not self.selection_spaces:
            return hv.Points(dset, ["cs1", "cs2"]).opts(color="blue")
        colors = hv.Cycle('Category10').values
        plots = [
            hv.Points(dset, dims).opts(color=c)
            for c, dims in zip(colors, self.selection_spaces)
        ]
        
        layout = hv.Layout(plots).cols(6)
        lsp = hv.selection.link_selections.instance()
        self.linked_selection = lsp
        layout = self.linked_selection(layout)

        return layout

    @param.depends("linked_selection.selection_expr")
    def selection(self): 
        table = hv.Table(dset).opts(width=1550)
        
        if self.linked_selection and self.linked_selection.selection_expr:
            selected = table[self.linked_selection.selection_expr.apply(table)]
            self.events = selected.data
            return selected
        self.events = table.data
        return table

    def panel(self):
        date_picker =self.param.dates
        runs_picker = pn.widgets.MultiChoice(value=["181028_0045"], name="Runs",
            options=["181028_0045"], solid=False, width=1000)
        runs_picker.link(self, value="runs")
        source_picker = pn.widgets.CheckButtonGroup(value=["None"], name="Source",
            options=["None", "AmBe", "NG", "Rn220"])
        source_picker.link(self, value="source")

        selection_spaces = pn.widgets.CheckButtonGroup(value=self.DIMS, name="Selection spaces",
            options={f"{x} vs {y}": [x,y] for x,y in self.DIMS}, width=1000)
        selection_spaces.link(self, value="selection_spaces")
        
        return pn.Column(
            pn.layout.Divider(),
            pn.pane.Markdown("## First allow the user to load events by date range/run_id/source"),
            date_picker,
            runs_picker,
            pn.pane.Markdown("  Source"),
            source_picker,
            pn.layout.Divider(),
            pn.pane.Markdown("## Allow user to choose the selection spaces of interest e.g. cut spaces, energy etc."),
            selection_spaces,
            pn.pane.Markdown("## Plot events in selection spaces of interest for user to apply selections."),
            pn.panel(self.event_selection),
            pn.layout.Divider(),
            pn.pane.Markdown("## Preview selected events with properties"),
            self.selection,
            width=1600,)


class WaveformBrowser(param.Parameterized):
    events = param.DataFrame(default=pd.DataFrame())

    def peak_plot(self, index):
        print(index)
        if not index:
            index = [0]
        events = self.event_table.iloc[index].data
        all_peaks = np.load("181028_0045_peaks.npy")
        peaks = strax.split_by_containment(all_peaks, events.to_records())
        # print(peaks[0])
        plots =[]
        for i, peak in enumerate(peaks):
            if len(peak["data"]) and len(peak["data"])<30:
                ymax = np.max(peak["data"])
                overlay = hv.NdOverlay({j:hv.Curve(peak["data"][k], kdims='digtizer index', vdims="counts").opts(width=500, interpolation="steps-mid", xlim=(0,200), ylim=(0,ymax)) for j, k in enumerate(reversed(np.argsort(peak["area"])))})
                plots.append(overlay)
        return hv.Layout(plots)

    @param.depends("events", watch=True)
    def panel(self):
        self.event_table = hv.Table(self.events)
        selected = hv.streams.Selection1D(source=self.event_table)
        tags = pn.widgets.MultiChoice(value=["Weird"], name="Tags",
            options=["Weird", "Very weird", "Super weird", "Uber weird", "Weird with a cherry on top"], solid=False, width=700)
        event_browser = pn.Row(self.event_table, hv.DynamicMap(self.peak_plot, streams=[selected]))
        comments = pn.widgets.input.TextAreaInput(name='Comments', placeholder='Add some extra comments...', height=500)
        return pn.Column(
            pn.pane.Markdown("## Make a nice interactive app to browse through the waveforms grouped by event and maybe some other options for grouping..."),
            pn.layout.Divider(),
            event_browser,
            pn.layout.Divider(),
            pn.pane.Markdown("## Allow for adding tags and comments and track them for each waveform."),
            tags,
            comments,
        )
        
class Saver(param.Parameterized):
    def panel(self):
        return pn.pane.Markdown("# Allow user to review their tagging and comments before saving them to DB")

stages = [
    ("Find events", WaveformWatcher),
    ("Browse Waveforms", WaveformBrowser), 
    ("Save to DB", Saver), 
]

pipeline = pn.pipeline.Pipeline(stages, debug=True, inherit_params=True)
view = pn.Column(
    pn.pane.Markdown("## When you are done selecting events press the 'Next' button."),
    pn.layout.Divider(width=1600),
    pipeline.layout,
    
    width=1600
)
view.servable()
