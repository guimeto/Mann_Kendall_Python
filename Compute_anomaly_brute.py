# -*- coding: utf-8 -*-
"""
Created on Thu May  2 09:59:07 2019

@author: guillaume
"""
import pandas as pd
import pathlib

##########################-- Partie du code à modifier --######################
yearmin = 1970                                                         #
yearmax = 2019                                                          #                                                                                                    
varin = 'Tasmoy'                    # Tasmax, Tasmin, Tasmoy      
indice = 'MOY' 
list_nom = pd.read_csv('K:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_noms_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.csv',usecols = [1])
path_m = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_MONTH/'+str(varin)+'/MOY/'+str(yearmin)+'_'+str(yearmax)+'/'
path_clim_m = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_MONTH/'+str(varin)+'/MOY/1990_2019/' 

path_s = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_SEASON/'+str(varin)+'/MOY/'+str(yearmin)+'_'+str(yearmax)+'/'
path_clim_s = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_SEASON/'+str(varin)+'/MOY/1990_2019/' 

path_y = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_YEAR/'+str(varin)+'/MOY/'+str(yearmin)+'_'+str(yearmax)+'/'
path_clim_y = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_YEAR/'+str(varin)+'/MOY/1990_2019/' 

# Travail sur les données mensuelles
for month in range(1,13,1):    
    for  index, row in list_nom.iterrows():
        data = pd.read_csv(path_m + row[0] + '_MONTH_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_'+str('{:02d}'.format(month))+'.csv', skiprows=2)
        data = data.rename(columns={ data.columns[1]: "var" }).set_index('datetime') 
        data_clim = pd.read_csv(path_clim_m + row[0] + '_MONTH_'+varin+'_'+indice+'_1990_2019_'+str('{:02d}'.format(month))+'.csv', skiprows=2)
        data_clim = data_clim.rename(columns={ data_clim.columns[1]: "var" }).set_index('datetime')   
        modDfObj = data.apply(lambda x: x - data_clim.mean()  , axis=1)
        
        mypath_month='K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_MONTH/ANOMALY_BRUTE/'+varin+'/'+str(indice)+'/'+str(yearmin)+'_'+str(yearmax)+'/'   
        pathlib.Path(mypath_month).mkdir(parents=True, exist_ok=True)
        modDfObj.to_csv(mypath_month+row[0]+'_ANO_STD_MONTH_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_'+str('{:02d}'.format(month))+'.csv')
       
# Travail sur les données saisonnieres
        
for season in ['DJF','JJA','MAM','SON']:       
    for  index, row in list_nom.iterrows():
        data = pd.read_csv(path_s + row[0] + '_SEASON_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_'+season+'.csv', skiprows=0)
        data =  data.rename(columns={ data.columns[2]: "var" }).set_index('Date') 
        data.drop(data.columns[0], axis=1, inplace=True)
        data_clim = pd.read_csv(path_clim_s + row[0] + '_SEASON_'+varin+'_'+indice+'_1990_2019_'+season+'.csv', skiprows=0)
        data_clim = data_clim.rename(columns={ data_clim.columns[2]: "var" }).set_index('Date')  
        data_clim.drop(data_clim.columns[0], axis=1, inplace=True)
        
        modDfObj = data.apply(lambda x: x - data_clim.mean()   , axis=1)
        modDfObj
        mypath_s='K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_SEASON/ANOMALY_BRUTE/'+varin+'/'+str(indice)+'/'+str(yearmin)+'_'+str(yearmax)+'/'   
        pathlib.Path(mypath_s).mkdir(parents=True, exist_ok=True)
        modDfObj.to_csv(mypath_s+row[0]+'_ANO_STD_SEASON_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_'+season+'.csv')

# Travail sur les données annuelles
                      
for  index, row in list_nom.iterrows():
    data = pd.read_csv(path_y + row[0] + '_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'_YEAR.csv', skiprows=0)
    data =  data.rename(columns={ data.columns[2]: "var" }).set_index('Date') 
    data.drop(data.columns[0], axis=1, inplace=True)
    data_clim = pd.read_csv(path_clim_y + row[0] + '_'+varin+'_'+indice+'_1990_2019_YEAR.csv', skiprows=0)
    data_clim = data_clim.rename(columns={ data_clim.columns[2]: "var" }).set_index('Date')  
    data_clim.drop(data_clim.columns[0], axis=1, inplace=True)
    
    modDfObj = data.apply(lambda x: x - data_clim.mean()  , axis=1)
    mypath_y='K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_YEAR/ANOMALY_BRUTE/'+varin+'/'+str(indice)+'/'+str(yearmin)+'_'+str(yearmax)+'/'   
    pathlib.Path(mypath_y).mkdir(parents=True, exist_ok=True)
    modDfObj.to_csv(mypath_y+row[0]+'_ANO_STD_YEAR_'+varin+'_'+indice+'_'+str(yearmin)+'_'+str(yearmax)+'.csv')



