# -*- coding: utf-8 -*-
"""
Rug Plot Demonstration Script.

This script demonstrates how to create a rug plot in conjunction with a
distribution plot (histogram and Kernel Density Estimate) using Matplotlib
and Seaborn.

The script performs the following main steps:
1.  Generates a sample dataset of 1000 points from a normal distribution
    (mean=10, std_dev=2).
2.  Sets up two vertically stacked subplots that share a common x-axis:
    a.  The top subplot (`a`) is used to display the distribution of the data
        using `seaborn.distplot()`.
    b.  The bottom subplot (`a2`) is used to display the rug plot, where
        individual data points are marked with short vertical lines ('|')
        along the x-axis. This subplot has its y-ticks removed.
3.  Applies styling using `seaborn` (`white` style, `poster` context).
4.  Includes an option (`despline = True`) to customize the plot's appearance
    by removing spines and ticks. If `despline` is True:
    -   The top plot (`a`) has its left and bottom spines removed, and y-ticks
        are hidden.
    -   The bottom rug plot (`a2`) has its left spine removed.
    If `despline` is False, it uses a more standard `seaborn.despine()` behavior.
5.  The x-axis tick labels of the top plot (`a`) are hidden, as the shared
    x-axis is primarily represented by the rug plot below it.

The script is intended as an example of creating such composite plots and
showcases some customization options available with Seaborn and Matplotlib.
It does not define any reusable functions or classes but directly executes
the plotting procedure.
"""
# Original header comment:
# Spyder Editor
#
# This is a temporary script file.

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

despline = True

sns.set_style('white',)
sns.set_context('poster',font_scale=1.4)
plt.figure()

dis = np.random.normal(10,2,1000)
#a = plt.subplot(211)
a = plt.axes([.1, .2, .8, .7])
#a2 = plt.subplot(212, sharex=a)
a2 = plt.axes([.1,.1,.8,.1], sharex=a)

a2.set_yticks([])
a2.plot(dis,np.zeros_like(dis),marker='|',ms=30,mew=1, ls="None", alpha=0.4)

sns.distplot(dis,ax=a)

if despline:
    sns.despine(ax=a2,left=True)
    sns.despine(ax=a,left=True, bottom=True)
    a.yaxis.set_ticks([])
else:
    sns.despine(ax=a2,right=False)
    sns.despine(ax=a,right=False, bottom=True, top=False)
    a.yaxis.set_ticks_position('left')




a.xaxis.set_ticks_position('bottom')
plt.setp( a.get_xticklabels(), visible=False)