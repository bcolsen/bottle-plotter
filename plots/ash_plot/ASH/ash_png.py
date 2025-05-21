#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:34:19 2016

@author: bcolsen
"""
from __future__ import division, print_function
# import peirce  # Unused
from ash import ash
import base64
import sys
from io import BytesIO
import argparse
# from itertools import combinations # Unused
# import scipy.stats as stats # Unused
import seaborn as sns
import numpy as np
# import pandas as pd # Unused
import pylab as plt

import matplotlib
# chose a non-GUI backend
matplotlib.use('Agg')


plt.rcParams['svg.fonttype'] = 'none'

'''
cli
'''
data = ('-0.38763, 0.80928, 1.5736, -0.19156, -1.2762, 0.012471, 2.7392, '
        '-0.14373, 1.5309, -0.71012, 2.6883, -0.97024, -0.18379, 0.39052, '
        '0.89383, -0.28856, -0.82227, -1.2461, 2.8595, 0.50082')

# ==============================================================================
# parser = argparse.ArgumentParser()
# parser.add_argument("test", help="Test label")
# parser.add_argument("thick", type=float,
#                     help="As-spun polymer thickness in nm")
# #parser.add_argument("--no_wait", action="store_true",
# #                    help="Starts anneal time as soon as solvent flow starts")
# parser.add_argument("--type", type=str, choices=test_type_list,
#                     help="Type of test")
# parser.add_argument('--step', type=float,  action='append', nargs=3,
#                     metavar = ('swell', 'dwell', 'rate'),
#                     help="Takes 3 floats: Desired swelling ratio, Anneal "
#                          "dwell time in seconds, ramp rate in swelling "
#                          "ratio per minute. If you need multiple steps "
#                          "define --step multiple times")
# ==============================================================================

# ==============================================================================
parser = argparse.ArgumentParser()
parser.add_argument("data", type=str, help="Test data, comma sep numbers")

args = parser.parse_args()

# print('args: ', args)
data = args.data
# ==============================================================================

# ==============================================================================
# '''
# perice code
# '''
# # number of outliner
# m=2
#
# PCE_PC_a = peirce.PeirceCriteria(test_file['PCE'],m)
# print( PCE_PC_a.RejVec, test_file[PCE_PC_a.RejVec], PCE_PC_a.AcceptVec)
#
# PCE_PC_b = peirce.PeirceCriteria(test_file2['PCE'],m)
# print( PCE_PC_b.RejVec, test_file2[PCE_PC_b.RejVec], PCE_PC_b.AcceptVec)
#
# ==============================================================================

sns.set(style='ticks', font='Arial', context='talk', font_scale=1.2)


fig = plt.figure(num='JV Dist', figsize=(6, 6))
fig.clf()

a = np.array(data.split(','), dtype=float)
# a = np.array(data_fake.split(','), dtype=float)

# a = np.array(test_file[PCE_PC_a.AcceptVec])
# b = np.array(test_file2[PCE_PC_b.AcceptVec][col])

bins = None

ash_obj_a = ash(a, bin_num=bins, force_scott=True)
# ash_obj_b = ash(b, bin_num=bins, force_scott = True)

ax = plt.subplot(111)

# plot ASH as a line

ax.plot(ash_obj_a.ash_mesh, ash_obj_a.ash_den, lw=2, color='#365994')
# ax.plot(ash_obj_b.ash_mesh,ash_obj_b.ash_den,lw=2, color = '#D95319')

# plot the solid ASH
ash_obj_a.plot_ash_infill(ax, color='#92B2E7')
# ash_obj_b.plot_ash_infill(ax, color ='#F2966E')

# plot KDE
#    ax.plot(ash_obj_a.kde_mesh,ash_obj_a.kde_den,lw=2)
#    ax.plot(ash_obj_b.kde_mesh,ash_obj_b.kde_den,lw=2, color = '#D95319')

# barcode like data representation
ash_obj_a.plot_rug(ax, alpha=1, color='#4C72B0')

# ash_obj_a.plot_rug(ax, alpha=1, color = '#4C72B0', ms = 8, height = 0.10)
# ash_obj_b.plot_rug(ax, alpha=1, color ='#F2966E', ms = 8, height = 0.04)

# ==============================================================================
# if ash_obj_a.mean <= ash_obj_b.mean:
#     ash_obj_a.plot_stats(ax, col, color = '#365994')
#     #ash_obj_b.plot_stats(ax, col, side='right', color ='#D95319')
# else:
#
#     #ash_obj_b.plot_stats(ax, col, color ='#D95319')
# ==============================================================================

# ash_obj_a.plot_stats(ax, side='right', color = '#365994')

# add a line showing the expected distribution
#    dist = plt.normpdf(ash_obj.ash_mesh, mu, sigma)
#    plt.plot(ash_obj.ash_mesh,dist,'r--',lw=2)
#    plt.plot(ash_obj.ash_mesh,dist-ash_obj.ash_den,'r--',lw=2)

# ax.spines['right'].set_visible(False)
# ax.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.tick_params(direction='out')
ax.set_yticks([])
#    ax.spines['top'].set_visible(False)
#    ax.spines['right'].set_visible(False)
#    ax.spines['left'].set_visible(False)
# print(ash_obj_a.mean, ash_obj_a.sigma)
# ad_stat, ad_crit, ad_signi = stats.anderson_ksamp((a,b))
# print('ad', ad_stat, ad_crit, ad_signi)
# ks_stat, ks_signi = stats.ks_2samp(a,b)
# print('ks', ks_stat, ks_signi)
# print(ash_obj_a.bw, ash_obj_a.bin_num, ash_obj_a.bin_width,
#       ash_obj_a.bin_edges[1]-ash_obj_a.bin_edges[0])
# print(ash_obj_b.bw, ash_obj_b.bin_num, ash_obj_b.bin_width,
#       ash_obj_b.bin_edges[1]-ash_obj_b.bin_edges[0])
# ad_ks_str = "p = {:.2f} %".format(ad_signi*100, ks_signi*100)
# p value text
# ax.text(0.05, 0.75, ad_ks_str, color='k', ha='left', va='center',
#         transform=ax.transAxes, size=14)
plt.xlabel('test')

plt.tight_layout()
plt.subplots_adjust(top=0.95)
# fig.text(0.47, 0.97, label, size=18, color='#365994', ha='right')
# fig.text(0.5, 0.97, 'vs.', size=18, ha='center')
# fig.text(0.53, 0.97, label2, size=18, color='#D95319', ha='left')
outs = BytesIO()
plt.show()
fig.savefig(outs, dpi=300, transparent=True)

sys.stdout.write(base64.b64encode(outs.getvalue()).decode('ascii'))

# col_list2 = ['PCE','Jsc','Voc','FF','Rsh', 'Rs']
#
# fig = plt.figure('Correlations2', figsize=(25,15))
# fig.clf()
# gs_axes = gridspec.GridSpec(3, 5)
#
# for (a, b), gs in zip(combinations(col_list2, 2), gs_axes):
#    a_vals = np.array(test_file[PCE_PC_a.AcceptVec][a])
#    b_vals = np.array(test_file[PCE_PC_a.AcceptVec][b])
#    ax = plt.subplot(gs)
#    ax.scatter(a_vals,b_vals, color= '#4C72B0')
#    ax.text(0.05, 0.95,'{:.2f}'.format(np.corrcoef(a_vals,b_vals)[0,1]*100),
#            color='#4C72B0', ha='left', va='top', transform=ax.transAxes,
#            size=16)
#
#    a_vals = np.array(test_file2[PCE_PC_b.AcceptVec][a])
#    b_vals = np.array(test_file2[PCE_PC_b.AcceptVec][b])
#    ax.scatter(a_vals,b_vals, color= '#D95319')
#    ax.text(0.95, 0.95,'{:.2f}'.format(np.corrcoef(a_vals,b_vals)[0,1]*100),
#            color='#D95319', ha='right', va='top', transform=ax.transAxes,
#            size=16)
#    ax.set_title(b+'-'+a)
#    ax.tick_params(direction='in')
#
# plt.tight_layout()


# plt.show()
