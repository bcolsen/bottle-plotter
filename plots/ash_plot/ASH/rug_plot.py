# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

despline = True

sns.set_style('white',)
sns.set_context('poster', font_scale=1.4)
plt.figure()

dis = np.random.normal(10, 2, 1000)
# a = plt.subplot(211)
a = plt.axes([.1, .2, .8, .7])
# a2 = plt.subplot(212, sharex=a)
a2 = plt.axes([.1, .1, .8, .1], sharex=a)

a2.set_yticks([])
a2.plot(
    dis,
    np.zeros_like(dis),
    marker='|',
    ms=30,
    mew=1,
    ls="None",
    alpha=0.4)

sns.distplot(dis, ax=a)

if despline:
    sns.despine(ax=a2, left=True)
    sns.despine(ax=a, left=True, bottom=True)
    a.yaxis.set_ticks([])
else:
    sns.despine(ax=a2, right=False)
    sns.despine(ax=a, right=False, bottom=True, top=False)
    a.yaxis.set_ticks_position('left')


a.xaxis.set_ticks_position('bottom')
plt.setp(a.get_xticklabels(), visible=False)
