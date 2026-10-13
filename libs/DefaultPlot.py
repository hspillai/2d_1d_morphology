import matplotlib.pyplot as plt 
import matplotlib.tri as tri
import numpy as np

def set_defaults_2(plt, font_size = 12, line_width = 1, marker_size = 5,
                   major_tick_size = 3.5, minor_tick_size = 2.):
    preamblelist = [#helvelt
        r'\usepackage{helvet}',  # uses helvetica ~ arial for latex fonts (we set matplotlib to use latex all over the place below ;))
        # r'\usepackage{mathptmx}',   # this would use times new roman for math ...
        r'\usepackage{amsmath}',
        r'\usepackage{amsthm}',
        r'\usepackage{amssymb}',
        r'\usepackage{amsfonts}',        
#        r'\usepackage[EULERGREEK]{sansmath}',
#        r'\sansmath', 
        r'\renewcommand{\rmdefault}{\sfdefault}',  # I don't know what this is useful for
        r'\usepackage{bm}', # bold math with \bm{some formula} Do not use this, just use mathbf!
    ]

    rcdict = {
        
        'figure.figsize': (3.75, 3.75), # this is a common paper fig. size
        'font.size': font_size, #12
        'lines.linewidth': line_width,
        'lines.markersize': marker_size,

        'text.latex.preamble': '\n'.join(preamblelist),
        'text.usetex': True,

#       'text.usetex': True,

        'font.family': 'sans-serif',
        'font.sans-serif': ['Helvetica', 'helvet'], #['Helvetica', 'helvet'],
		# some axes labeling and ticking
        'axes.labelsize': font_size,
        'xtick.labelsize': font_size,
        'ytick.labelsize': font_size,

		# make the ticks point inside (this is what we want ;) )
        'xtick.direction': 'in',
        'xtick.major.size': major_tick_size,
        'xtick.minor.size': minor_tick_size,
        'xtick.minor.visible': True,
        'xtick.top': True,
        
        'ytick.direction': 'in',
        'ytick.major.size': major_tick_size,
        'ytick.minor.size': minor_tick_size,
        'ytick.minor.visible': True,
        'ytick.right': True,
    }

	# first restore the defaults
    plt.rcdefaults()

	# now update them to what we want
    plt.rcParams.update(rcdict)

def set_defaults(plt):
    preamblelist = [#helvelt
        r'\usepackage{helvet}',  # uses helvetica ~ arial for latex fonts (we set matplotlib to use latex all over the place below ;))
        # r'\usepackage{mathptmx}',   # this would use times new roman for math ...
        r'\usepackage{amsmath}',
        r'\usepackage[EULERGREEK]{sansmath}',
        r'\sansmath', 
        # r'\renewcommand{\rmdefault}{\sfdefault}',  # I don't know what this is useful for
        # r'\usepackage{bm}', # bold math with \bm{some formula} Do not use this, just use mathbf!
    ]

    rcdict = {

        'figure.figsize': (3.25, 3.25), # this is a common paper fig. size
            'font.size': 9,
            'lines.linewidth': 1,
            'lines.markersize': 5,

		# we don't need this, because font stuff is managed by latex!
            # 'font.family':          'serif',
            # 'font.family':          'sans-serif',
            # 'font.family':            'STIXGeneral',
            # 'font.sans-serif':      ['Computer Modern Serif'],
            # 'font.sans-serif':      ['Helvetica', 'helvet'],
            # 'mathtext.fontset':     'cm',
            # 'mathtext.fontset':     'stixsans',
            # 'mathtext.fontset': 'stix',

		# tell it to use latex
            'text.latex.preamble': '\n'.join(preamblelist),
            'text.usetex': True,

		# some axes labeling and ticking
            'axes.labelsize': 9,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,

		# make the ticks point inside (this is what we want ;) )
            'xtick.direction': 'in',
            'xtick.major.size': 3.5,
            'xtick.minor.size': 2.,
            'xtick.minor.visible': True,
            'xtick.top': True,

        'ytick.direction': 'in',
            'ytick.major.size': 3.5,
            'ytick.minor.size': 2.,
            'ytick.minor.visible': True,
            'ytick.right': True,
    }

	# first restore the defaults
    plt.rcdefaults()

	# now update them to hat we want
    plt.rcParams.update(rcdict)

def set_panel_labels(panel_labels, axs):
    '''
    panel_labels is a list of panel labels i.e. [a, b, c, d] 
    '''

    for count, label in enumerate(panel_labels):
        label_tmp =  r'$\rm \bf {f}$'.format(f = label)        
        axs[count].text(-0.1, 1.05,
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


paper_path = '/home/pillai/68833c3c01ab96b7821d513b/figures/raw_figures/'
poster_path = '/home/pillai/emrs_slides/Figures_3/pdfs/'
