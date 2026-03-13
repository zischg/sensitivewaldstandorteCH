import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd


#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi/export"
#projectspace="C:/DATA"
climatescenarios=['rcp45','rcp85']

#impoirt kantone
kantone_gdf=gpd.read_file(projectspace+"/kantone.gpkg", layer='kantone')
kantone_gdf.columns
kantonsliste=kantone_gdf['kanton'].unique().tolist()
kantonsliste.sort()
kantonsliste.remove('TI')
len(kantonsliste)

#export sensitive standorte kantone
for climatescenario in climatescenarios:
    print(climatescenario)
    infile = gpd.read_file(projectspace + "/klimasensitive_standorte_" + climatescenario + "_kantone.gpkg")
    for kanton in kantonsliste:
        print(kanton)
        extract_gdf=infile[infile['kanton']==kanton]
        extract_gdf.to_file(projectspace+"/Kantone/"+kanton+"_klimasensitive_standorte_" + climatescenario + ".gpkg", layer=kanton+"_klimasensitive_standorte_" + climatescenario, driver="GPKG")


#export Baumartenempfehlungen kantone
for climatescenario in climatescenarios:
    print(climatescenario)
    infile = gpd.read_file(projectspace + "/baumartenempfehlung_" + climatescenario + "_kantone.gpkg")
    for kanton in kantonsliste:
        print(kanton)
        extract_gdf=infile[infile['kanton']==kanton]
        extract_gdf.to_file(projectspace+"/Kantone/"+kanton+"_baumartenempfehlung_" + climatescenario + ".gpkg", layer=kanton+"_baumartenempfehlung_" + climatescenario, driver="GPKG")

#export sensitive Bestaende kantone
for climatescenario in climatescenarios:
    print(climatescenario)
    infile = gpd.read_file(projectspace + "/klimasensitive_bestaende_fi_" + climatescenario + ".gpkg")
    kantoneliste=infile['kanton'].unique().tolist()
    kantoneliste.sort()
    kantoneliste.remove('TI')
    for kanton in kantoneliste:
        print(kanton)
        extract_gdf=infile[infile['kanton']==kanton]
        extract_gdf.to_file(projectspace+"/Kantone/"+kanton+"_klimasensitive_bestaende_fi_" + climatescenario + ".gpkg", layer=kanton+"_klimasensitive_bestaende_fi_" + climatescenario, driver="GPKG")






