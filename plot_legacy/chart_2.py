import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from local_library import DataSegmentType, plot_data_segment, thousands_formatter, load_data, GraphResultType, GraphType, InitialAngle, AngleType, ClassicalAlgorithm
import local_library
from get_data import get_dataset

# define constants
#export_path = 'C:\\Bikini Atoll\\QUANTUM\\Thesis Imagery C 1-2\\'
export_path = 'C:\\Bikini Atoll\\QUANTUM\\BACKUP 20251120\\projects\\ex09\\_out20260228\\_graph\\_dissertation_charts2\\'


def draw_chart(ia=InitialAngle.All, graphType = GraphType.All, testIndex = 'D', layers = 1, graph_result_type = GraphResultType.CC, classical_algo = ClassicalAlgorithm.All, save:bool = True):
    figwidth = 13

    match graph_result_type:
        case GraphResultType.CC:
            y_axis_title = 'Number of Evaluations'
            figwidth = 13
            if testIndex == 'COMPARE1-2':
                local_library.do_thousands_formatter = 0
            else:
                local_library.do_thousands_formatter = 1000
            local_library.max_y = -1

        case GraphResultType.AR:
            y_axis_title = 'Approximation Ratio'
            figwidth = 12.5
            local_library.do_thousands_formatter = 1
            local_library.max_y = 1

        case GraphResultType.AP:
            y_axis_title = 'Actual Probability'
            figwidth = 12.5
            local_library.do_thousands_formatter = 0
            local_library.max_y = 100

    if testIndex in {'A', 'B', 'AB'}:
        figwidth *= 2

    # load from CSV
    #prefix = 'd-'  # Prefix for filenames
    #data_ma = load_data(f'{prefix}data-ma.csv')
    #data_am = load_data(f'{prefix}data-am.csv')
    #data_ka = load_data(f'{prefix}data-ka.csv')
    #data_sa = load_data(f'{prefix}data-sa.csv')

    # load from database
    if testIndex == 'COMPARE1-2':
        data_ma = get_dataset(ia, graphType, testIndex, layers, AngleType.SingleAngle, graph_result_type, classical_algo, True)
        data_sa = get_dataset(ia, graphType, testIndex, layers, AngleType.SingleAngle, graph_result_type, classical_algo, False)
    else:
        data_ma = get_dataset(ia, graphType, testIndex, layers, AngleType.MultiAngle, graph_result_type, classical_algo)
        data_am = get_dataset(ia, graphType, testIndex, layers, AngleType.AutomorphicAngle, graph_result_type, classical_algo)
        data_ka = get_dataset(ia, graphType, testIndex, layers, AngleType.KAngle, graph_result_type, classical_algo)
        data_sa = get_dataset(ia, graphType, testIndex, layers, AngleType.SingleAngle, graph_result_type, classical_algo)

    '''
    print('ma ****************************')
    print(data_ma)
    print('ka ****************************')
    print(data_ka)
    print('sa ****************************')
    print(data_sa)
    print('am ****************************')
    print(data_am)
    '''

    # Adjust figure size dynamically based on number of x-ticks 20250209
    #num_xticks = len(data_ma['n'])  # Adjust width proportionally to the number of x-ticks
    #figwidth = max(13, 0.8 * num_xticks)  # Use a minimum width, scaling it based on x-ticks

    # Create figure and axes with doubled size in inches
    fig, ax1 = plt.subplots(figsize=(figwidth, 7.6))

    # Plot Segments
    plot_data_segment(ax1, data_ma, DataSegmentType.MA)
    if testIndex != 'COMPARE1-2':
        plot_data_segment(ax1, data_am, DataSegmentType.AM)
    if testIndex != 'COMPARE1-2':
        plot_data_segment(ax1, data_ka, DataSegmentType.KA)
    plot_data_segment(ax1, data_sa, DataSegmentType.SA)

    # Tighten layout and save 20250209
    #plt.tight_layout()  # Removes extra spaces around the plot
    # Adjust layout with custom margins 20250209
    if testIndex == "AB":
        plt.subplots_adjust(left=0.06, right=0.99, top=0.99)  # Increase left margin and slightly tighten right margin
    else:
        plt.subplots_adjust(left=0.13, right=0.99, top=0.99, bottom=0.14)  # Increase left margin and slightly tighten right margin

    # Set x-axis label based on testIndex, but data remains 'n'
    x_axis_label = 'p' if testIndex in ['C', 'D'] else 'n'

    # Set the x-ticks using 'n' data, but conditionally change the label
    ax1.set_xticks(data_ma['n'].astype(int))  # Keep the x-ticks based on 'n' data
    ax1.set_xticklabels(data_ma['n'].astype(int), fontsize=30)  # Ensure tick labels are integers
    ax1.set_xlabel(x_axis_label, fontsize=30)  # Change the x-axis label to 'p' or 'n'

    # Increase font size for y-axis labels and numbers
    if testIndex == "AB":
        ax1.set_ylabel(y_axis_title, fontsize=30)
        ax1.tick_params(axis='y', labelsize=30)  # Increase y-axis numbers font size
    else:
        ax1.set_ylabel(y_axis_title, fontsize=20)
        ax1.tick_params(axis='y', labelsize=20)  # Increase y-axis numbers font size

    # Add grid
    ax1.grid(True, which='both', linestyle='--', linewidth=0.7)

    # Format y-axis labels to be divided by 1000
    ax1.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    if save:
        img_name  = f'plot_{graph_result_type.name}'
        img_name += f'_g{graphType.name}' if testIndex in ['A', 'B', 'AB'] else ''
        img_name += f'_p{layers}' if testIndex in ['A', 'B', 'AB', 'COMPARE1-2'] else ''
        img_name += '' if ia == InitialAngle.All else f'_a{ia.name}'
        img_name += '' if classical_algo == ClassicalAlgorithm.All else f'_a{classical_algo.name}'
        img_name += f'_x{testIndex}'
        img_name += '.png'
        print(img_name)
        plt.savefig(export_path + img_name, format='png', dpi=300)
    else:
        plt.show()

    # Close the figure to free memory
    plt.close(fig)


def draw_all_charts(ia=InitialAngle.All, graphType=GraphType.All, testIndex='D', layers=2, classical_algo = ClassicalAlgorithm.All, save:bool=True):
    draw_chart(ia, graphType, testIndex, layers, GraphResultType.AR, classical_algo, save)
    if testIndex != 'COMPARE1-2':
        draw_chart(ia, graphType, testIndex, layers, GraphResultType.AP, classical_algo, save)
    draw_chart(ia, graphType, testIndex, layers, GraphResultType.CC, classical_algo, save)


#draw_chart(graph_result_type=GraphResultType.AR, testIndex='AB', graphType=GraphType.Path, save=False, layers=1)
#draw_all_charts(testIndex='C')
draw_all_charts(testIndex = 'COMPARE1-2', graphType=GraphType.All, layers = 1)
draw_all_charts(testIndex = 'COMPARE1-2', graphType=GraphType.All, layers = 2)
draw_all_charts(testIndex = 'COMPARE1-2', graphType=GraphType.All, layers = 3)
draw_all_charts(testIndex = 'COMPARE1-2', graphType=GraphType.All, layers = 4)
draw_all_charts(testIndex = 'COMPARE1-2', graphType=GraphType.All, layers = 5)
#quit()

draw_all_charts(testIndex = 'AB', graphType=GraphType.All, layers = 2, classical_algo = ClassicalAlgorithm.POWELL)
draw_all_charts(testIndex = 'AB', graphType=GraphType.All, layers = 2, classical_algo = ClassicalAlgorithm.BFGS)

draw_all_charts(testIndex = 'AB', graphType=GraphType.Path, layers = 1)
draw_all_charts(testIndex = 'AB', graphType=GraphType.Path, layers = 2)
draw_all_charts(testIndex = 'AB', graphType=GraphType.Path, layers = 3)

draw_all_charts(testIndex = 'AB', graphType=GraphType.Cyclic, layers = 1)
draw_all_charts(testIndex = 'AB', graphType=GraphType.Cyclic, layers = 2)
draw_all_charts(testIndex = 'AB', graphType=GraphType.Cyclic, layers = 3)

draw_all_charts(testIndex = 'AB', layers = 1)
draw_all_charts(testIndex = 'AB', layers = 2)
draw_all_charts(testIndex = 'AB', layers = 3)

#C
draw_all_charts(testIndex='C')

#D
draw_all_charts(testIndex='D')

#IA
draw_all_charts(InitialAngle.F1P, testIndex = 'AB', layers = 1)
#draw_all_charts(InitialAngle.F1P, testIndex = 'AB', layers = 2)
#draw_all_charts(InitialAngle.F1P, testIndex = 'AB', layers = 3)

draw_all_charts(InitialAngle.R01P, testIndex = 'AB', layers = 1)
#draw_all_charts(InitialAngle.R01P, testIndex = 'AB', layers = 2)
#draw_all_charts(InitialAngle.R01P, testIndex = 'AB', layers = 3)

draw_all_charts(InitialAngle.R02PIP, testIndex = 'AB', layers = 1)
#draw_all_charts(InitialAngle.R02PIP, testIndex = 'AB', layers = 2)
#draw_all_charts(InitialAngle.R02PIP, testIndex = 'AB', layers = 3)

draw_all_charts(InitialAngle.TQA, testIndex = 'AB', layers = 1)
#draw_all_charts(InitialAngle.TQA, testIndex = 'AB', layers = 2)
#draw_all_charts(InitialAngle.TQA, testIndex = 'AB', layers = 3)

draw_all_charts(InitialAngle.F1P, testIndex = 'C')
draw_all_charts(InitialAngle.R01P, testIndex = 'C')
draw_all_charts(InitialAngle.R02PIP, testIndex = 'C')
draw_all_charts(InitialAngle.TQA, testIndex = 'C')

draw_all_charts(InitialAngle.F1P, testIndex = 'D')
draw_all_charts(InitialAngle.R01P, testIndex = 'D')
draw_all_charts(InitialAngle.R02PIP, testIndex = 'D')
draw_all_charts(InitialAngle.TQA, testIndex = 'D')
