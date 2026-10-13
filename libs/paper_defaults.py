import matplotlib as mpl
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from matplotlib.colors import LinearSegmentedColormap, LogNorm
import numpy as np

light_green = [198./255, 211./255, 37./255]
green = [0./255, 108./255, 102./255]
dark_green = [0.0/255, 85./255, 85./255]

light_blue  = [0./255., 177./255., 234./255.]
blue = [0./255., 106./255., 234./255.]
dark_blue   = [41./255., 72./255., 93./255.]

orange      = [239./255., 124./255., 0./255.]

fhicmap_blue =  LinearSegmentedColormap.from_list('fhicmap_blue', [dark_blue, blue, light_blue], 512 * 2)
fhicmap_green =  LinearSegmentedColormap.from_list('fhicmap_green', [dark_blue, green, light_green], 512 * 2)

fhicmap_blue_green =  LinearSegmentedColormap.from_list('fhicmap_blue', [light_blue, blue, dark_green], 512 * 2)

def add_text_to_ax(ax, x, y, txt, **kwargs):
    """
    Add text elements to a matplotlib.axes element

    Parameters
    ==========
    ax:     matplotlib.axis
        The subplot element in which you want to add the text element.
    x:      float
        Relative x-axis position of the text element.
    y:      float
        Relative y-axis position of the text element.
    txt:    str,
        The text that you wish to write on the subplot.
    kwargs:
        fontsize:   float,
        color:      str,
        horizontalalignment:    str, default = 'right'
        verticalalignment:      str, default = 'top'
    """
    pe = [path_effects.withStroke(linewidth=1, foreground='w')]
    txt_kwargs = {
        'fontsize': 10.5, 'color': 'k',
        'horizontalalignment': 'right', 'verticalalignment': 'top',
        'transform': ax.transAxes, 'path_effects': pe
    }
    txt_kwargs.update(kwargs)
    ax.text(x, y, txt, **txt_kwargs)
    return None

def set_paper_params(font_size=12,
                     line_width=1,
                     marker_size=5,
                     major_tick_size=3.5,
                     minor_tick_size=2,
                     label_pad = 4.0):

    black       = [0., 0., 0.]
    dark_green  = [0./255., 108./255., 102./255.]
    dark_blue   = [41./255., 72./255., 93./255.]
    light_green = [198./255., 211./255., 37./255.]
    light_blue  = [0./255., 177./255., 234./255.]
    orange      = [239./255., 124./255., 0./255.]
    red         = [192./255., 0., 0.]
    blue        = [0., 112./255., 192./255.]
    green       = [0., 176./255., 82./255.]

#    fhicmap =  LinearSegmentedColormap.from_list('fhicmap', [light_blue, 'white', orange], 512)
    fhicmap =  LinearSegmentedColormap.from_list('fhicmap', [dark_blue, light_blue], 512)
    fhicmap2 =  LinearSegmentedColormap.from_list('fhicmap2', [dark_green, light_green], 512)

    ratio = 12./12.
    textcolor = black

    old_preamblelist =  [
        r'\usepackage{helvet}',
        r'\usepackage{bm}',
        r'\usepackage{amsmath}',
        #r'\usepackage{mathptmx}', #If you want arial, comment out
        r'\usepackage[EULERGREEK]{sansmath}',
        r'\sansmath',
        r'\usepackage{siunitx}',
        r'\sisetup{detect-all}',
        r'\sisetup{detect-family = true}',
    ]

    preamblelist =  [
        r'\usepackage{helvet, bm}',
        r'\usepackage{amsmath}',
        r'\usepackage{sansmath}',
        #r'\usepackage{sansmathfonts}',
        r'\sansmath',
        r'\usepackage{siunitx}',
        r'\sisetup{detect-all}',
        r'\sisetup{detect-family = true}',
    ]

    rcdict =    {
        "axes.edgecolor":       textcolor,
        "axes.labelcolor":      textcolor,
        "axes.titlepad":        6.0 * ratio,
        "axes.labelpad":        label_pad, #4.0 * ratio,
#        'figure.figsize':       (5.2 *ratio, 3.9 * ratio),
        'font.family':          'sans-serif',
        'font.sans-serif':      ['Arial'],
        'font.size':            font_size,
        'lines.linewidth':      line_width,
        'lines.markersize':     marker_size,
        'mathtext.bf':          'stixsans:bold', #'stixsans',
        'mathtext.fontset':     'stixsans', #'stixsans',
        'mathtext.it':          'stixsans:italic', #'stixsans',
        'mathtext.rm':          'stixsans', #'stixsans',
        'mathtext.sf':          'stixsans', #'stixsans',
        "text.color":           textcolor,
        'text.latex.preamble':  '\n'.join(preamblelist),
        'text.usetex':          True,
        "xtick.color":          textcolor,
        'xtick.direction':      'in',

        'xtick.major.pad':      3.5 * ratio,

        'xtick.major.size': major_tick_size,
        'xtick.minor.size': minor_tick_size,
        'xtick.minor.pad':      3.4 * ratio,
        'xtick.minor.visible':  True,
        'xtick.top':            True,
        "ytick.color":          textcolor,
        'ytick.direction':      'in',
        'ytick.major.size':     major_tick_size,
        'ytick.major.pad':      3.5 * ratio,
        'ytick.minor.size':     minor_tick_size,
        'ytick.minor.pad':      3.4 * ratio,
        'ytick.minor.visible':  True,
        'ytick.right':          True,
        'axes.prop_cycle':      mpl.cycler(color=[
            dark_blue,
            light_green,
            red,
            blue, 
            orange,
            green, 
            light_blue,
            orange,
            dark_green,
            "pink",
            "cyan"
            ]),
        #'image.cmap':           fhicmap2,
    }
    plt.rcParams.update(rcdict)
    return None


def set_panel_labels(panel_labels, axs):
    '''
    panel_labels is a list of panel labels i.e. [a, b, c, d] 
    '''

    for count, label in enumerate(panel_labels):
        label_tmp =  r'$\rm \bf {f}$'.format(f = label)        
        axs[count].text(0, 0,
                        label_tmp, transform = axs[count].transAxes,
                        ha = 'right')
        
    return axs


def PlotContour_fromDict(ax, inx, data_dict, levels = 5):

    cords = data_dict[inx]['cords']
    values = data_dict[inx]['values']
    R, r, l = data_dict[inx]['params']

    # --- Mirror points across y-axis ---
    reflected_cords = cords.copy()
    reflected_cords[:, 0] = -reflected_cords[:, 0]  # reflect x → -x
    reflected_values = values.copy()

    # Concatenate original + reflected
    cords = np.vstack([cords, reflected_cords])

    values = np.concatenate([values, reflected_values])
#    values = np.vstack([values, reflected_values])

    x = cords[:, 0] * 1e6
    y = cords[:, 1] * 1e6
    triang = tri.Triangulation(x, y)
    x2 = x[triang.triangles].mean(axis=1) 
    y2 = y[triang.triangles].mean(axis=1)

    cond = x2**2 + y2**2 >= (r * 1e6)**2
    mask = np.where(cond, 0, 1)
    triang.set_mask(mask)
    
    ax.tricontour(triang,
                  values/max(values),
                  levels = levels,
                  linewidths = 0.85, colors = 'k')
    
    contour = ax.tricontourf(triang,
                             values/max(values), levels = levels)

    

    return ax, contour 

def set_panel_labels_2(panel_labels, axs, left_align_ax=None,
                     offset_x=-0.02, offset_y=0.02, fontsize=10):
    """
    Place panel labels outside axes in figure coordinates.

    - panel_labels: list of strings like ['a)', 'b)', 'c)', 'd)']
    - axs: list of axes in the same order as labels
    - left_align_ax: if provided, the first (top) label will align
                     with this axis' left edge instead of its own
    - offset_x, offset_y: offsets added to the axes' bbox coordinates
                          (both in figure coordinate units, ~0..1)
    - fontsize: text size
    """
    fig = axs[0].figure

    # reference left edge for aligning the first (wide-top) label
    ref_x0 = None
    if left_align_ax is not None:
        ref_x0 = left_align_ax.get_position().x0

    for idx, ax in enumerate(axs):
        bbox = ax.get_position()

        if idx == 0 and ref_x0 is not None:
            base_x = ref_x0
        else:
            base_x = bbox.x0

        # compute desired fig coords
        x = base_x + offset_x
        y = bbox.y1 + offset_y

        # clamp so label stays on canvas (very small margins)
        x = max(0.005, min(x, 0.99))
        y = max(0.01, min(y, 0.99))

        fig.text(x, y,
                 r'$\bf{{{}}}$'.format(panel_labels[idx]),
#                 panel_labels[idx],
                 fontsize=fontsize,
                 fontweight='bold',
                 ha='left', va='bottom')

    return axs

SI_paper_path = '/home/pillai/68833c3c01ab96b7821d513b/SI/figures/'
paper_path = '/home/pillai/68833c3c01ab96b7821d513b/figures/raw_figures/'
poster_path = '/home/pillai/emrs_slides/Figures_3/pdfs/'

