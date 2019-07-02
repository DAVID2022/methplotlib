import plotly
from plotly import tools
import methplotlib.plots as plots
import methplotlib.utils as utils
from methplotlib.import_methylation import get_data


def main():
    args = utils.get_args()
    windows = utils.make_windows(args.window)
    for window in windows:
        meth_data = get_data(args.methylation, args.names, window, args.smooth)
        correlation_plot(meth_data, window)
        meth_browser(meth_data=meth_data,
                     window=window,
                     gtf=args.gtf,
                     simplify=args.simplify,
                     split=args.split,
                     )


def meth_browser(meth_data, window, gtf=False, simplify=False, split=False):
    """
    methlist is a list of files from calculate_methylation_frequency
    names should have the same length as methlist and contain identifiers for the datasets
    annotation is optional and is a gtf, which will be processed by parse_gtf()

    if the traces are split per sample,
     then show one line per sample and one for the annotation
    if no splitting is done,
     then 4/5 of the browser is used for overlayed samples and one for annotation
    the trace to be used for annotation is thus methrows + 1
    """
    data = plots.methylation(meth_data)
    if split or data.split:
        methrows = len(meth_data)
        annot_axis = 'yaxis{}'.format(methrows + 1)
        fig = tools.make_subplots(rows=methrows + 1,
                                  cols=1,
                                  shared_xaxes=True,
                                  specs=[[{}] for i in range(methrows + 1)],
                                  print_grid=False
                                  )
        for position, sample_traces in enumerate(data.traces, start=1):
            for meth_trace in sample_traces:
                fig.append_trace(trace=meth_trace, row=position, col=1)
    else:
        methrows = 4
        annot_axis = 'yaxis2'
        fig = tools.make_subplots(rows=methrows + 1,
                                  cols=1,
                                  shared_xaxes=True,
                                  specs=[[{'rowspan': methrows}], [None], [None], [None], [{}], ],
                                  print_grid=False
                                  )
        for meth_trace in data.traces:
            fig.append_trace(trace=meth_trace[0], row=1, col=1)
    fig["layout"]["xaxis"].update(tickformat='g', separatethousands=True)
    if gtf:
        annotation_traces, y_max = plots.annotation(gtf, window, simplify)
        for annot_trace in annotation_traces:
            fig.append_trace(trace=annot_trace, row=methrows + 1, col=1)
        fig["layout"][annot_axis].update(range=[-1, y_max + 1],
                                         showgrid=False,
                                         zeroline=False,
                                         showline=False,
                                         ticks='',
                                         showticklabels=False)
        fig["layout"]["xaxis"].update(range=[window.begin, window.end])
    fig["layout"].update(barmode='overlay',
                         title="Nucleotide modifications",
                         hovermode='closest',
                         legend=dict(orientation='h'))
    with open("methylation_browser_{}.html".format(window.string), 'w') as output:
        output.write(plotly.offline.plot(fig,
                                         output_type="div",
                                         show_link=False)
                     )


def correlation_plot(meth_data, window):
    data = [m for m in meth_data if m.data_type == "frequency"]
    if len(data) < 2:
        return
    else:
        with open("methylation_frequency_correlation_{}.html".format(window.string), 'w') as output:
            output.write(plotly.offline.plot(plots.splom(meth_data),
                                             output_type="div",
                                             show_link=False)
                         )


if __name__ == '__main__':
    main()
