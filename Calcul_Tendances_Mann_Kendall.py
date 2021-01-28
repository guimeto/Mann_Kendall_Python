# -*- coding: utf-8 -*-
"""
Created on Thu May  2 09:59:07 2019

@author: guillaume
"""
import pandas as pd
import pathlib
import numpy as np
import pymannkendall as mk
import datetime

#for plotting

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib.pylab as plt
from carto import *
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
import warnings
warnings.filterwarnings("ignore")

#######################-- Partie du code à modifier --######################
yearmin = 1970                                                        #
yearmax = 2019   
dt=(yearmax-yearmin)+1                                                       #                                                                                                    
varin = 'Tasmoy'                    # Tasmax, Tasmin, Tasmoy      
indice = 'MOY' 
list_nom = pd.read_csv('F:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_noms_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.csv',usecols = [1])
list_latlon = pd.read_csv('F:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_latlon_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.csv',usecols = [1,2])
path_m = 'F:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_MONTH/'+str(varin)+'/MOY/'+str(yearmin)+'_'+str(yearmax)+'/'
path_trend_m = 'F:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/TREND_MONTH/'+str(varin)+'/MOY/'+str(yearmin)+'_'+str(yearmax)+'/' 

path_fig  = 'F:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/TREND_MONTH/figures/'+str(varin)+'/MOY/'+str(yearmin)+'_'+str(yearmax)+'/'

metDict = {
                'MK':{'name':'Original Mann-Kendall test', 
                      'code':'original_test'} ,
                'HR':{'name':'Hamed and Rao Modified MK Test', 
                      'code':'hamed_rao_modification_test'} ,
                'YW':{'name':'Yue and Wang Modified MK Test', 
                      'code':'yue_wang_modification_test'} ,
                'PW':{'name':'Modified MK test using Pre-Whitening method',
                      'code':'pre_whitening_modification_test'} ,
                'TFPW':{'name':'Modified MK test using Trend free Pre-Whitening method',
                        'code':'trend_free_pre_whitening_modification_test'} }


def plot_background(ax):
    ax.set_extent([-140,-50,32,82])  
    ax.coastlines(resolution='110m');
    ax.add_feature(cfeature.OCEAN.with_scale('50m'), zorder=1)      
    ax.add_feature(cfeature.LAND.with_scale('50m'))       
    ax.add_feature(cfeature.LAKES.with_scale('50m'))     
    ax.add_feature(cfeature.BORDERS.with_scale('50m'))    
    ax.add_feature(cfeature.RIVERS.with_scale('50m'))    
    coast = cfeature.NaturalEarthFeature(category='physical', scale='10m',    
                        facecolor='none', name='coastline')
    ax.add_feature(coast, edgecolor='black')
    
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='10m',
        facecolor='none')

    ax.add_feature(states_provinces, edgecolor='gray') 
    return ax

for cle,valeur in metDict.items(): # la boucle for obtient un tuple à chaque itération
    print(valeur['name']) 
    # Travail sur les données mensuelles
    for month in range(1,13,1):
        name_month = datetime.date(1900, int(month), 1).strftime('%B')
        
        TREND=[]    
        for  index, row in list_nom.iterrows():
            data = pd.read_csv(path_m + row[0] + '_MONTH_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_'+str('{:02d}'.format(month))+'.csv', skiprows=2)
            data = data.rename(columns={ data.columns[1]: "var" }).set_index('datetime') 
            
            if (valeur['name'] == 'Original Mann-Kendall test'):
                trend, h, p, z, Tau, s, var_s, slope, intercept = mk.original_test(data)
            elif (valeur['name'] == 'Hamed and Rao Modified MK Test'):
                trend, h, p, z, Tau, s, var_s, slope, intercept = mk.hamed_rao_modification_test(data)
            elif (valeur['name'] == 'Yue and Wang Modified MK Test'):
                trend, h, p, z, Tau, s, var_s, slope, intercept = mk.yue_wang_modification_test(data)
            elif (valeur['name'] == 'Modified MK test using Pre-Whitening method'):
                trend, h, p, z, Tau, s, var_s, slope, intercept = mk.pre_whitening_modification_test(data)
            elif (valeur['name'] == 'Modified MK test using Trend free Pre-Whitening method'):
                trend, h, p, z, Tau, s, var_s, slope, intercept = mk.trend_free_pre_whitening_modification_test(data)
                
            if (p >= 0.1):   # aucune tendance n'a été détectée 
                     slope=np.nan                             
            TREND.append(slope*10) 
            
        trend = pd.DataFrame({'trend':TREND})
        
        df= pd.concat([list_nom,trend,list_latlon], axis=1)       
        pathlib.Path(path_trend_m  + cle +'/').mkdir(parents=True, exist_ok=True)
        df.to_csv(path_trend_m + cle +'/INDICES_MONTH_'+valeur['code']+'_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_'+str('{:02d}'.format(month))+'.csv')
        
        fig=plt.figure(figsize=(30,18), frameon=True)    
        
        crs=ccrs.LambertConformal()
        ax = plt.axes(projection=crs)
        
        plot_background(ax)
        cmap = plt.cm.jet  # define the colormap
        norm = mpl.colors.BoundaryNorm(np.arange(-2,2.1,0.5), cmap.N)
        # Plots the data onto map
        plt.scatter(df['Longitude'][(df['trend'] > 0)], 
                    df['Latitude'][(df['trend'] > 0)],
                    alpha=1.,
                    s=800, label="Tmoy Trend",
                    c=df['trend'][(df['trend'] > 0)],
                    vmin=-2,
                    vmax=2,
                    cmap=cmap,
                    norm=norm,
                    transform=ccrs.PlateCarree(),
                    marker="^", zorder=10)
        
        mm =plt.scatter(df['Longitude'][(df['trend'] < 0)], 
                    df['Latitude'][(df['trend'] < 0)],
                    alpha=1.,
                    s=800, label="Tmoy Trend",
                    c=df['trend'][(df['trend'] < 0)],
                    vmin=-2,
                    vmax=2,
                    cmap=cmap,
                    norm=norm,
                    transform=ccrs.PlateCarree(),
                    marker="v", zorder=10)
        fig.canvas.draw()
        xticks = [-200, -180, -160, -140, -120, -100, -80, -60 ,-40, -20, 0]
        yticks = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
        ax.gridlines(xlocs=xticks, ylocs=yticks, linewidth=1, color='gray')
        ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
        ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)
        lambert_xticks(ax, xticks)
        lambert_yticks(ax, yticks)
    
      
        ax.text(-55., 40.,  u'\u25B2\nN', color='black', fontsize=30, transform=ccrs.Geodetic())
        
        string_title=u'Theil-Sen estimator/slope \n Month mean Tmoy [Celcius]\n (p-value 90%)\n ' + str(valeur['name']) +'\n' + name_month+' from ' + str(yearmin) +' to '+ str(yearmax)+'\n'
        plt.title(string_title, size='xx-large', fontsize=30)
        cbar = plt.colorbar(mm,  shrink=0.75, drawedges='True', ticks=np.arange(-2, 2.0, .5), extend='both',label='Températures (°C)')
        cbar.ax.tick_params(labelsize=17) 
        ax = cbar.ax
        text = ax.yaxis.label
        font = mpl.font_manager.FontProperties(size=25)
        text.set_font_properties(font)
        path_fig_new = path_fig + cle +'/'
        pathlib.Path(path_fig_new).mkdir(parents=True, exist_ok=True)
        
        plt.savefig(path_fig_new+'/'+str(cle)+'_Tendances_'+indice+'_'+varin+'_'+name_month+'_CANADA_'+str(yearmin)+'_'+str(yearmax)+'_90p.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()
    
    
    
    
    
    
    
    
    
       