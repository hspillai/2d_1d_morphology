
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap, LogNorm
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib.tri as tri
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset

import pandas as pd
import numpy as np
import os
import sys

sys.path.append('./../../libs/')

from paper_defaults import set_paper_params, set_panel_labels_2
from ReadData import CustomData

set_paper_params(font_size = 10,
                 label_pad = 1.5)

data_path = '/home/pillai/morphology_2d_1d/cylinderical/hemisphere/realL/Heatmap_4/results/'

data = CustomData(pandas_path=data_path).scale_column('sel', 100).sort_by('rho').add_ratio_column('r/L', 'r', 'L')
data.calculate_loading()

isolated_data_path = '/home/pillai/morphology_2d_1d/cylinderical/hemisphere/realL/Heatmap_4/figure4_b/isolated_particle/results/'
isolated_data = CustomData(pandas_path=isolated_data_path).scale_column('sel', 100).sort_by('rho').add_ratio_column('r/L', 'r', 'L')

# for each particle radius make a copy of the datapoint at a smaller roughness
# this is to simulate the plateuing behavior.
isolated_data.df["source"] = "original"
df_copy = isolated_data.df.copy()
df_copy["source"] = "modified"
isolated_df = pd.concat([isolated_data.df, df_copy], ignore_index=True)
isolated_df.loc[isolated_df["source"] == "modified", "rho"] *= 0.001
isolated_data.df = isolated_df
isolated_data.calculate_loading()
#isolated_df = isolated_data.df

results_1d = np.load('/home/pillai/morphology_2d_1d/one_dim/results.npy',
                     allow_pickle = True)
results_1d_df = pd.DataFrame(results_1d,
                             columns = ['rho', 'L', 'flux_intermediate', 'flux_prod',
                                        'selectivity_1d'])
results_1d_df['selectivity_1d'] *= 100

large_L = 25e-6
large_L_1d = results_1d_df[np.isclose(results_1d_df.L , large_L)]
large_L_1d = large_L_1d.sort_values(by = 'rho')

small_L = 5e-6
small_L_1d = results_1d_df[np.isclose(results_1d_df.L , small_L)]
small_L_1d = small_L_1d.sort_values(by = 'rho')

r_want = np.array([0.75e-6, 1.5e-6, 2.5e-6]) 
colors = ['blue', 'red', 'green']
fig, axs = plt.subplots(nrows = 2,
                        ncols = 2,
                        sharey = 'row',
                        gridspec_kw = {'width_ratios': [6, 2],
                                       'wspace': 0.05}
                        )

axs[0, 0].plot(large_L_1d.rho,
               large_L_1d.selectivity_1d)

axs[0, 1].plot(large_L_1d.rho,
               large_L_1d.selectivity_1d)

axs[1, 0].plot(small_L_1d.rho,
               small_L_1d.selectivity_1d)

axs[1, 1].plot(small_L_1d.rho,
               small_L_1d.selectivity_1d)
for left, right in [(axs[0,0], axs[0,1]),
                    (axs[1,0], axs[1,1])]:

    left.spines['right'].set_visible(False)
    right.spines['left'].set_visible(False)

    # Remove ticks on the broken side
    left.tick_params(axis = 'y',
                     which = 'both',
                     right=False,)

    right.tick_params(axis = 'y',
                      which = 'both',
                      left=False)

    # Remove y tick labels on right panel
    right.tick_params(labelleft=False)

# d = 0.015
# for left, right in [(axs[0,0], axs[0,1]),
#                     (axs[1,0], axs[1,1])]:

#     kwargs = dict(color='k',
#                   clip_on=False,
#                   lw=1.25)
#     # Right edge of left axis
#     left.plot((1-d, 1+d), (-d, +d),
#               transform=left.transAxes,
#               **kwargs)
#     left.plot((1-d, 1+d), (1-d, 1+d),
#               transform=left.transAxes,
#               **kwargs)

#     # Left edge of right axis
#     right.plot((-d, +d), (-d, +d),
#                transform=right.transAxes,
#                **kwargs)
#     right.plot((-d, +d), (1-d, 1+d),
#                transform=right.transAxes,
#                **kwargs)
d = 0.5

kwargs = dict(
    marker=[(-1, -1), (1, 1)],
    markersize=5,
    linestyle="none",
    color='k',
    mec='k',
    mew=1.0,
    clip_on=False,
)

for left, right in [(axs[0,0], axs[0,1]),
                    (axs[1,0], axs[1,1])]:

    left.plot([1, 1], [0, 1], transform=left.transAxes, **kwargs)
    right.plot([0, 0], [0, 1], transform=right.transAxes, **kwargs)
    
axs[0, 0].xaxis.set_major_locator(ticker.MultipleLocator(0.4))
axs[0, 0].xaxis.set_minor_locator(ticker.MultipleLocator(0.1))

axs[0, 1].xaxis.set_major_locator(ticker.MultipleLocator(0.4))
axs[0, 1].xaxis.set_minor_locator(ticker.MultipleLocator(0.1))

axs[0, 0].yaxis.set_major_locator(ticker.MultipleLocator(20))
axs[0, 0].yaxis.set_minor_locator(ticker.MultipleLocator(5))


axs[1, 0].xaxis.set_major_locator(ticker.MultipleLocator(0.4))
axs[1, 0].xaxis.set_minor_locator(ticker.MultipleLocator(0.1))

axs[1, 1].xaxis.set_major_locator(ticker.MultipleLocator(0.4))
axs[1, 1].xaxis.set_minor_locator(ticker.MultipleLocator(0.1))

axs[1, 0].yaxis.set_major_locator(ticker.MultipleLocator(20))
axs[1, 0].yaxis.set_minor_locator(ticker.MultipleLocator(5))

ticks = axs[0, 0].get_xticks()
axs[0, 0].set_xticks(ticks[:-1])  # remove rightmost tick

ticks = axs[0, 1].get_xticks()
axs[0, 1].set_xticks(ticks[1:])   # remove leftmost tick


ticks = axs[1, 0].get_xticks()
axs[1, 0].set_xticks(ticks[:-1])  # remove rightmost tick

ticks = axs[1, 1].get_xticks()
axs[1, 1].set_xticks(ticks[1:])   # remove leftmost tick

shift = [0.10, 0.18]
for count, r in enumerate(r_want):
    color = colors[count]
    for count, L in enumerate([large_L, small_L]):
        df_ = data.df[(data.df.r == r) & (data.df.L == L)]
        if len(df_) == 0:
            continue
        iso_df_ = isolated_df[(isolated_df.r == r) & (isolated_df.L == L)]

        label = str(r * 1e6)
        
        axs[count, 0].annotate(rf'$r_{{\rm p}}$ = {label} \textmu m',#label,
                               (df_.rho.values[0] + shift[count], df_.sel.values[0]) ,
#                               df_1[['rho', 'sel']].values[0] + [0.08, 0],
                               color = color)
        
        axs[count, 0].plot(iso_df_.rho,
                           iso_df_.sel,
                           c = color)

        axs[count, 1].plot(iso_df_.rho,
                           iso_df_.sel,
                           c = color)

        
        axs[count, 0].scatter(df_.rho,
                              df_.sel, label = r * 1e6,
                              c= color)

        axs[count, 1].scatter(df_.rho,
                              df_.sel, label = r * 1e6,
                              c= color)
        

        axs[count, 0].plot(df_.rho,
                           df_.sel,
                           c= color)
        axs[count, 1].plot(df_.rho,
                           df_.sel,
                           c= color)
        

axs[0, 0].set_xlim(0, 1.1)
axs[0, 1].set_xlim(1.75, 2.0)

axs[1, 0].set_xlim(0, 1.1)
axs[1, 1].set_xlim(1.75, 2.0)

axs[0, 0].set_ylim(0, 100)
axs[1, 0].set_ylim(0, 100)
#axs[0, 0].set_xlabel(r'Roughness, $\rho$')
axs[0, 0].set_ylabel(r'$\rm Selectivity\ CO/C_{1} + C_{2+} (\%)$')

#axs[1, 0].set_xlabel(r'Roughness, $\rho$')
axs[1, 0].set_ylabel(r'$\rm Selectivity\ CO/C_{1} + C_{2+} (\%)$')

fig.set_size_inches(1 * 3.75,
                    1.3 * 3.75) # width, height 

fig.tight_layout(rect=[0, 0.02, 1, 0.98])
fig.subplots_adjust(hspace=0.5)
#axs[2].set_axis_off()
for row in [0, 1]:
    left = axs[row, 0]
    right = axs[row, 1]

    # Get position of both axes in figure coordinates
    bbox_left = left.get_position()
    bbox_right = right.get_position()

    x_center = (bbox_left.x0 + bbox_right.x1) / 2
    y = bbox_left.y0 - 0.04  # tweak vertical offset

    fig.text(
        x_center,
        y,
        r'Roughness, $\rho$',
        ha='center',
        va='top'
    )


fig.tight_layout()

axs[0, 1].text(1.70, 85, r'$L_{\rm diff}$ = 25\ \textmu m',
            fontsize = 10)
axs[1, 1].text(1.70, 85, r'$L_{\rm diff}$ = 5\ \textmu m')


panel_labels = ['a)','b)']
set_panel_labels_2(panel_labels,
                 [axs[0, 0],
                  axs[1, 0]], offset_x = -0.15)

fig.show()
# fig.savefig(f'{paper_path}/fig2.pdf', dpi = 300, transparent = True)
# fig.savefig(f'{paper_path}/fig2.svg', dpi = 300, transparent = True)
