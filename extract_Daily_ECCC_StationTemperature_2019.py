# -*- coding: utf-8 -*-
"""
Created on Thu May  2 09:59:07 2019

@author: guillaume
"""
import pandas as pd
import os
from datetime import date
import calendar
import numpy as np
import pathlib

##########################-- Partie du code à modifier --######################
yearmin = 1990                                                              #
yearmax = 2010                                                              #
varin = 'dm'                                                                  #
path = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/Homog_daily_mean_temp_v2019'                                           #
varout = 'Tasmoy'                                                             #
###############################################################################

### lecture de toutes les stations d'ECCC pour la température
dataframe = pd.read_excel("./Homog_Temperature_Stations.xls", skiprows = range(0, 3))

### on va filtrer les données ayant pour période commune: yearmin - yearmax
globals()['dataframe_'+str(yearmin)+'_'+str(yearmax)] = dataframe.loc[(dataframe["année déb."] <= yearmin) & (dataframe["année fin."] >= yearmax),:]

## boucle sur chaque station et extraction des séries quotidiennes
names = []
for i, row in globals()['dataframe_'+str(yearmin)+'_'+str(yearmax)].iterrows():
   stnid = row['stnid']
   
   f1 = open(path+'/'+str(varin)+str(stnid)+'.txt', 'r')
   f2 = open('./tmp.txt', 'w')

### nettoyage des données   
   for line in f1:
        for word in line:
            if word == 'M':
                f2.write(word.replace('M', ' '))
            elif word == 'a':
                f2.write(word.replace('a', ' '))                    
            else:
                f2.write(word)
   f1.close()
   f2.close()
          
   station = pd.read_csv('./tmp.txt', delim_whitespace=True, skiprows = range(0, 4))
   
   station.columns = ['Annee', 'Mois', 'D1','D2','D3','D4','D5','D6','D7','D8','D9','D10',
                                  'D11','D12','D13','D14','D15','D16','D17','D18','D19','D20',
                                  'D21','D22','D23','D24','D25','D26','D27','D28','D29','D30','D31']
     
   os.remove("./tmp.txt")
   
   # nettoyage des valeurs manquantes 
   try:  
       station = station.replace({'E':''}, regex=True)
   except:
       pass
   try: 
       station = station.replace({'a':''}, regex=True)
   except:
       pass
   try:     
       station = station.replace({'-9999.9':''}, regex=True)
   except:
       pass
   try:     
       station = station.replace(-9999.9, np.nan)
   except:
       pass    
       
   for col in  station.columns[2:]:
       station[col] = pd.to_numeric(station[col], errors='coerce')
       
   m_start =  station['Mois'].loc[(station['Annee'] == yearmin)].min()
   m_end   =  station['Mois'].loc[(station['Annee'] == yearmax)].max()
   
   d_end = calendar.monthrange(yearmax, m_end)[1]
   
####################################Extraction des données quotidiennes  et ajout d'une colonne Date   
   tmp_tmin = [ ] 
   for year in range(yearmin,yearmax+1):    ### Boucle sur les annees
       for month in range(1,13):
           df = []
           last_day = calendar.monthrange(year, month)[1] 
           tmin = station.loc[(station["Annee"] == year) & (station["Mois"] == month)].iloc[:,2:last_day+2].values
           
           if len(tmin) == 0:
               a = np.empty((calendar.monthrange(year,month)[1]))
               a[:] = np.nan
               df=pd.DataFrame(a)
           else:
               df=pd.DataFrame(tmin.T)
               
           start = date(year, month, 1)
           end =   date(year, month, last_day)
           delta=(end-start) 
           nb_days = delta.days + 1 
           rng = pd.date_range(start, periods=nb_days, freq='D')          
           df['datetime'] = rng
           df.index = df['datetime']
           tmp_tmin.append(df)
           
   tmp_tmin = pd.concat(tmp_tmin)
   tmp_tmin.replace(-9999.9, np.nan, inplace=True)
   
   df = pd.DataFrame({'datetime': tmp_tmin['datetime'], 'Var': tmp_tmin.iloc[:,0]}, columns = ['datetime','Tmin']) 
   df.index = df['datetime']
   tmp_tmin = tmp_tmin.drop(["datetime"], axis=1)
      
   name = row['Nom de station'].replace(' ','_')
   name = name.replace("'",'')
   names.append(name)
   mypath='K:/DATA/Donnees_Stations/2nd_generation_V2019/Daily_data/'+varout+'/'+str(yearmin)+'_'+str(yearmax)+'/'
   pathlib.Path(mypath).mkdir(parents=True, exist_ok=True)
   
   tmp_tmin.to_csv(mypath+name+'_daily_'+varout+'_'+str(yearmin)+'-'+str(yearmax)+'.csv')
   
### ecriture d'un fichier latlon des stations traitées entre yearmin et yearmax         
latlon = pd.DataFrame({'Latitude': globals()['dataframe_'+str(yearmin)+'_'+str(yearmax)]["lat (deg)"], 'Longitude': globals()['dataframe_'+str(yearmin)+'_'+str(yearmax)]["long (deg)"] }, columns = ['Latitude','Longitude']) 
latlon.to_csv('K:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_latlon_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.csv')

id_station = pd.DataFrame({'ID': globals()['dataframe_'+str(yearmin)+'_'+str(yearmax)]["stnid"]}) 
id_station.to_csv('K:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_ID_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.csv')
base_filename = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_ID_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.txt'
id_station.to_csv(base_filename, sep='\t', index = False)


names = pd.DataFrame(names)
names.to_csv('K:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_noms_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.csv')

base_filename = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/TEMP_ID/stations_noms_CANADA_'+str(yearmin)+'-'+str(yearmax)+'.txt'
names[0].to_csv(base_filename, sep='\t', index = False)
