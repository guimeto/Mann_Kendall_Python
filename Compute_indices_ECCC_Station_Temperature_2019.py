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
import Indices_Temperatures
from dateutil.relativedelta import relativedelta
import pathlib

##########################-- Partie du code à modifier --######################
yearmin = 1963                                                        #
yearmax = 2015                                                          #
varin = 'dx'                         # dx, dn, dm                                                           
path = 'K:/DATA/Donnees_Stations/2nd_generation_V2019/Homog_daily_max_temp_v2019'#'Homog_daily_max_temp_v2018'   'Homog_daily_min_temp_v2018'  'Homog_daily_mean_temp_v2018'                                            
varout = 'Tasmax'                    # Tasmax, Tasmin, Tasmoy      
list_indices = ['MOY']                                                             
###############################################################################
for ind in list_indices:
    
    if ind == 'MOY':
       indice = Indices_Temperatures.MOY  
       indice_out = 'MOY'     
    elif ind == 'Tmax90p':
       indice = Indices_Temperatures.Tmax90p
       indice_out = 'Tmax90p'
    elif ind == 'Tmin10p':
       indice = Indices_Temperatures.Tmin10p
       indice_out = 'Tmin10p'
       
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
           station = station.replace({'-9999.9':np.nan}, regex=True)
       except:
           pass
       try:     
           station = station.replace(-9999.9, np.nan)
           #station.replace({-9999.9:''}, regex=True)
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
       
       df = pd.DataFrame({'datetime': tmp_tmin['datetime'], 'variable': tmp_tmin.iloc[:,0]}, columns = ['datetime','variable']) 
       df.index = df['datetime']  
    #################################### Calcul des indices mensuels     
       resamp_tmin = df.resample('M').agg([indice ])     
 
    #################################### Calcul des indices saisonniers  
       
       djf = []
       mam = []
       son=[]
       jja=[]
       incr= date(yearmin, 1, 1)
       end = date(yearmax, 12, 31)
       while incr <= end:
            current_year = str(incr.year)
            last_year = str(incr.year-1)
            try:
                dec = df[last_year][np.in1d(df[last_year].index.month, [12])]
            except:
                rng = pd.date_range(last_year, periods=31, freq='D')
                dec = pd.DataFrame({'datetime': rng, 'variable': [np.nan]*31}, columns = ['datetime','variable']) 
                
            j_f = df[current_year][np.in1d(df[current_year].index.month, [1,2])]
               
            djf.append(indice(dec.append(j_f).iloc[:,1].values))
            
            mam.append(indice((df[current_year][np.in1d(df[current_year].index.month, [3,4,5])].iloc[:,1]).values))
            jja.append(indice((df[current_year][np.in1d(df[current_year].index.month, [6,4,8])].iloc[:,1]).values))
            son.append(indice((df[current_year][np.in1d(df[current_year].index.month, [9,10,11])].iloc[:,1]).values))
              
            incr = incr + relativedelta(years=1)
    
    #################################### Calcul des indices annuels  
       annual = []
       df_annual = []
       incr= date(yearmin, 1, 1)
       end = date(yearmax, 12, 31)
       while incr <= end:
            current_year = str(incr.year)
            annual.append(indice(df[current_year].iloc[:,1].values))         
            incr = incr + relativedelta(years=1)
            
    #################################### Écriture des indices en format csv     
       TIME=[]
       for y in range(yearmin,yearmax+1,1):
            TIME.append(y) 
       df_annual = pd.DataFrame({'Date': TIME,'Indice': annual}, columns = ['Date','Indice Annuel']) 
            
    #################################### Écriture des indices en format csv 
       mypath_saison='K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_SEASON/'+varout+'/'+str(indice_out)+'/'+str(yearmin)+'_'+str(yearmax)+'/'
       pathlib.Path(mypath_saison).mkdir(parents=True, exist_ok=True)
       
       mypath_month='K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_MONTH/'+varout+'/'+str(indice_out)+'/'+str(yearmin)+'_'+str(yearmax)+'/'
       pathlib.Path(mypath_month).mkdir(parents=True, exist_ok=True)
       
       mypath_year='K:/DATA/Donnees_Stations/2nd_generation_V2019/INDICES/INDICES_YEAR/'+varout+'/'+str(indice_out)+'/'+str(yearmin)+'_'+str(yearmax)+'/'
       pathlib.Path(mypath_year).mkdir(parents=True, exist_ok=True)
       
       TIME=[]
       for y in range(yearmin,yearmax+1,1):
            TIME.append(y)
            
       df_annual = pd.DataFrame({'Date': TIME,'Indice Annuel': annual}, columns = ['Date','Indice Annuel']) 
         
       df_djf = pd.DataFrame({'Date': TIME,'Indice DJF': djf}, columns = ['Date','Indice DJF']) 
       df_mam = pd.DataFrame({'Date': TIME,'Indice MAM': mam}, columns = ['Date','Indice MAM']) 
       df_jja = pd.DataFrame({'Date': TIME,'Indice JJA': jja}, columns = ['Date','Indice JJA']) 
       df_son = pd.DataFrame({'Date': TIME,'Indice SON': son}, columns = ['Date','Indice SON']) 
          
       name = row['Nom de station'].replace(' ','_')
       name = name.replace("'",'')
       names.append(name)
       df_annual.to_csv(mypath_year+name+'_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_YEAR.csv')
      
       df_djf.to_csv(mypath_saison+name+'_SEASON_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_DJF.csv')
       df_mam.to_csv(mypath_saison+name+'_SEASON_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_MAM.csv')
       df_jja.to_csv(mypath_saison+name+'_SEASON_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_JJA.csv')
       df_son.to_csv(mypath_saison+name+'_SEASON_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_SON.csv') 
          
       for m in range(1,13):
           month_var = resamp_tmin[resamp_tmin.index.month==m]
           
           np.savetxt(mypath_month+name+'_MONTH_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_'+str("{:02}".format(m))+'.txt', month_var, fmt="%5.2f", newline='\n')
           
           month_var.to_csv(mypath_month+name+'_MONTH_'+varout+'_'+indice_out+'_'+str(yearmin)+'_'+str(yearmax)+'_'+str("{:02}".format(m))+'.csv')
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
