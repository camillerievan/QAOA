import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from local_library import DataSegmentType, plot_data_segment, thousands_formatter, load_data, GraphResultType, GraphType, InitialAngle, AngleType
import local_library
from get_data import get_dataset

# define constants
#export_path = 'C:\\Bikini Atoll\\QUANTUM\\Thesis Imagery CLAL C\\'
export_path = 'C:\\Bikini Atoll\\QUANTUM\\BACKUP 20251120\\projects\\ex09\\_out20260228\\_graph\\_dissertation_charts\\'


def draw_chart(angleType:AngleType, testIndex = 'AB', graphType = GraphType.All, layers = 1, graph_result_type = GraphResultType.CC, save:bool = True):
    figwidth = 13

    match graph_result_type:
        case GraphResultType.CC:
            y_axis_title = 'Number of Evaluations'
            figwidth = 13
            local_library.do_thousands_formatter = True
            local_library.max_y = -1
        case GraphResultType.AR:
            y_axis_title = 'Approximation Ratio'
            figwidth = 12.5
            local_library.do_thousands_formatter = False
            local_library.max_y = 1
        case GraphResultType.AP:
            y_axis_title = 'Actual Probability'
            figwidth = 12.5
            local_library.do_thousands_formatter = False
            local_library.max_y = 100

    #if testIndex in {'A', 'B', 'AB'}:
    #    figwidth *= 2

    # load from CSV
    #prefix = 'd-'  # Prefix for filenames
    #data_ma = load_data(f'{prefix}data-ma.csv')
    #data_am = load_data(f'{prefix}data-am.csv')
    #data_ka = load_data(f'{prefix}data-ka.csv')
    #data_sa = load_data(f'{prefix}data-sa.csv')

    # load from database
    data_f1p = get_dataset(InitialAngle.F1P, graphType, testIndex, layers, angleType, graph_result_type)
    data_r01p = get_dataset(InitialAngle.R01P, graphType, testIndex, layers, angleType, graph_result_type)
    data_r02pip = get_dataset(InitialAngle.R02PIP, graphType, testIndex, layers, angleType, graph_result_type)
    data_tqa = get_dataset(InitialAngle.TQA, graphType, testIndex, layers, angleType, graph_result_type)

    '''
    print('f1p ****************************')
    print(data_f1p)
    print('r01p ****************************')
    print(data_r01p)
    print('r02pip ****************************')
    print(data_r02pip)
    print('tqa ****************************')
    print(data_tqa)
    '''

    # Create figure and axes with doubled size in inches
    fig, ax1 = plt.subplots(figsize=(figwidth, 7.6))

    # Plot Segments
    plot_data_segment(ax1, data_f1p, DataSegmentType.MA)
    plot_data_segment(ax1, data_r01p, DataSegmentType.AM)
    plot_data_segment(ax1, data_r02pip, DataSegmentType.KA)
    plot_data_segment(ax1, data_tqa, DataSegmentType.SA)

    # Set x-axis label based on testIndex, but data remains 'n'
    #x_axis_label = 'p' if testIndex in ['C', 'D'] else 'n'
    x_axis_label = 'n'

    # Set the x-ticks using 'n' data, but conditionally change the label
    ax1.set_xticks(data_f1p['n'].astype(int))  # Keep the x-ticks based on 'n' data
    ax1.set_xticklabels(data_f1p['n'].astype(int), fontsize=16)  # Ensure tick labels are integers
    ax1.set_xlabel(x_axis_label, fontsize=16)  # Change the x-axis label to 'p' or 'n'

    # Increase font size for y-axis labels and numbers
    ax1.set_ylabel(y_axis_title, fontsize=18)
    ax1.tick_params(axis='y', labelsize=16)  # Increase y-axis numbers font size

    # Add grid
    ax1.grid(True, which='both', linestyle='--', linewidth=0.7)

    # Format y-axis labels to be divided by 1000
    #ax1.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    if save:
        img_name  = f'plot_{graph_result_type.name}'
        #img_name += f'_g{graphType.name}' if testIndex in ['A', 'B', 'AB'] else ''
        #img_name += f'_p{layers}' if testIndex in ['A', 'B', 'AB'] else ''
        #img_name += '' if ia == InitialAngle.All else f'_a{ia.name}'
        #img_name += f'_x{testIndex}'
        img_name += '.png'
        print(img_name)
        plt.savefig(export_path + img_name, format='png', dpi=300)
    else:
        plt.show()

    # Close the figure to free memory
    plt.close(fig)


def draw_all_charts(angleType:AngleType, testIndex = 'AB', graphType=GraphType.All, layers=2, save:bool=True):
    draw_chart(angleType, testIndex, graphType, layers, GraphResultType.AR, save)
    draw_chart(angleType, testIndex, graphType, layers, GraphResultType.AP, save)
    draw_chart(angleType, testIndex, graphType, layers, GraphResultType.CC, save)


draw_all_charts(AngleType.KAngle, testIndex='AB', layers=2, save=True)
