import numpy as np
import pandas as pd
import joblib
import fiona
import geopandas as gpd
import os
import shapely
from osgeo import ogr
import xlrd
import openpyxl
import psycopg2
import warnings
from osgeo import osr, gdal
from sqlalchemy import create_engine
mypassword=input("Enter database password: ").replace("'","")
db_connection_url = "postgresql://azischg:"+mypassword+"@mobidb02.giub.unibe.ch:5432/ccwdb";
engine = create_engine(db_connection_url)
#con=engine.connect()
drv = gdal.GetDriverByName('GTiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(2056) #LV95
gtiff_driver=gdal.GetDriverByName("GTiff")
import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
winsound.Beep(frequency, duration)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
import matplotlib.pyplot as plt


#color dictionaries
# Define specific RGB colors for each class combination (normalized to [0,1])
sensisto_colors_dict = {
    -999: (110.0/255.0,110.0/255.0,114.0/255.0),  # Keine Angabe, Grau
    0: (30.0/255.0,41.0/255.0,235.0/255.0),      # Nicht klimasensitiv, Dunkles Blau
    1: (9.0/255.0,132.0/255.0,255.0/255.0),    # Schwach klimasensitiv, Helles Blau
    2: (237.0/255.0,171.0/255.0, 100.0/255.0),       # Mittel klimasensitiv, Orange
    3: (145.0/255.0,82.0/255.0,45.0/255.0)}      # Stark klimasensitiv, Braun

#sensisto_labels = ['Kein klimasensitiver Standort', 'Klimasensitiver Standort', 'Langfristig klimasensitiver Standort', 'Teilweise klimasensitiver Standort']
sensisto_labels = ['Keine Angabe', 'Nicht klimasensitiv', 'Schwach klimasensitiv', 'Mittel klimasensitiv', 'Stark klimasensitiv']#, 'Bedingt klimasensitiv'] Für alle Standorte mit Arven



#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
#projectspace="C:/DATA"
climatescenarios=['rcp45','rcp85']
#climatescenario="rcp85"
#climatescenario="rcp45"
#climatescenario="rcp26"

#import data from database
#Sensitive standorte
#rcp45
sql='SELECT * FROM public."rcp45_sensitivebestaende_FI_TBk_var1"'
sensisto_rcp45=gpd.read_postgis(sql, con=engine, geom_col='geom')
sensisto_rcp45.columns
storeg_list=sensisto_rcp45['storeg'].unique().tolist()
storeg_list.sort()
print(storeg_list)
len(sensisto_rcp45)
sensisto_rcp45=sensisto_rcp45[sensisto_rcp45['inanalysis']==1]
len(sensisto_rcp45)
tot_area=  sensisto_rcp45.geometry.area.sum()
# Area statistics CH
areastatistics_ch=sensisto_rcp45.groupby(['maxsens']).agg({'area_m2': 'sum'})
areastatistics_ch['area_tot_pct']=areastatistics_ch['area_m2']/tot_area*100
#areastatistics_ch['area_tot_ant']=areastatistics_ch['area_m2']/tot_area
areastatistics_ch.to_excel(projectspace+'/areastatistics_rcp45_sensitivebestaende_CH.xlsx')
#area statistics Standortregionen
areastatistics=sensisto_rcp45.groupby(['storeg','maxsens']).agg({'area_m2': 'sum'})
areastatistics['area_tot_pct']=areastatistics['area_m2']/tot_area*100
areastatistics.to_excel(projectspace+'/areastatistics_rcp45_sensitivebestaende_regionen.xlsx')
#create a pie chart for CH
labels_zahlen = areastatistics_ch.index.get_level_values('maxsens').tolist()
print(labels_zahlen)
print(sensisto_labels)
sizes= areastatistics_ch['area_tot_pct'].tolist()


# Create pie chart for CH RCP4.5 Sensitive Standorte
fig, ax = plt.subplots(figsize=(8, 6))
#ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
# Create pie chart
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=None,  # Remove labels from pie slices
    colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 12},
    pctdistance=0.85,
    counterclock=False)
# Equal aspect ratio
ax.axis('equal')
# Set title
ax.set_title('Klimasensitive Bestände FI RCP4.5 CH', fontsize=14, fontweight='bold',pad=20)
# CREATE CUSTOM LEGEND WITH LABELS
legend_labels = sensisto_labels
ax.legend(
    wedges,
    legend_labels,
    #title="Sensitive Standorte",
    loc="lower right",
    #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
    bbox_to_anchor=(1.2, 0),
    fontsize=9,
    title_fontsize=12,
    frameon=False,
    fancybox=False,
    shadow=False)
plt.tight_layout()
plt.savefig(projectspace+'/areastatistics_rcp45_sensitivebestaende_CH_piechart.png', dpi=300)
plt.show()

# Create pie chart for CH RCP4.5 Sensitive Standorte for each Standortregion
for region in storeg_list:
    print(region)
    tot_area_region=  sensisto_rcp45[sensisto_rcp45['storeg']==region].geometry.area.sum()
    areastatistics_region=sensisto_rcp45[sensisto_rcp45['storeg']==region].groupby(['maxsens']).agg({'area_m2': 'sum'})
    areastatistics_region['area_tot_pct'] = areastatistics_region['area_m2'] / tot_area_region * 100
    #labels_zahlen = areastatistics_region.index.get_level_values('sensisto').tolist()
    print(labels_zahlen)
    print(sensisto_labels)
    #sizes = areastatistics_region['area_tot_pct'].tolist()
    sizes=[]
    for key in labels_zahlen:
        if key in areastatistics_region.index:
            sizes.append(areastatistics_region.loc[key,'area_tot_pct'])
        else:
            sizes.append(0)
    print(sizes)
    fig, ax = plt.subplots(figsize=(8, 6))
    #ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,  # Remove labels from pie slices
        colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12},
        pctdistance=0.85,
        counterclock=False)
    # Equal aspect ratio
    ax.axis('equal')
    # Set title
    ax.set_title('Klimasensitive Bestände FI RCP4.5 Region '+region, fontsize=14, fontweight='bold',pad=20)
    # CREATE CUSTOM LEGEND WITH LABELS
    legend_labels = sensisto_labels
    ax.legend(
        wedges,
        legend_labels,
        #title="Sensitive Standorte",
        loc="lower right",
        #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
        bbox_to_anchor=(1.2, 0),
        fontsize=9,
        title_fontsize=12,
        frameon=False,
        fancybox=False,
        shadow=False)
    plt.tight_layout()
    plt.savefig(projectspace+'/areastatistics_rcp45_sensitivebestaende_piechart_'+region+'.png', dpi=300)
    plt.show()
#delete data
del(sensisto_rcp45)

#**********************************************************************************
#rcp85
sql='SELECT * FROM public."rcp85_sensitivebestaende_FI_TBk_var1"'
sensisto_rcp85=gpd.read_postgis(sql, con=engine, geom_col='geom')
sensisto_rcp85.columns
storeg_list=sensisto_rcp85['storeg'].unique().tolist()
storeg_list.sort()
print(storeg_list)
len(sensisto_rcp85)
sensisto_rcp85=sensisto_rcp85[sensisto_rcp85['inanalysis']==1]
len(sensisto_rcp85)
tot_area=  sensisto_rcp85.geometry.area.sum()
# Area statistics CH
areastatistics_ch=sensisto_rcp85.groupby(['maxsens']).agg({'area_m2': 'sum'})
areastatistics_ch['area_tot_pct']=areastatistics_ch['area_m2']/tot_area*100
#areastatistics_ch['area_tot_ant']=areastatistics_ch['area_m2']/tot_area
areastatistics_ch.to_excel(projectspace+'/areastatistics_rcp85_sensitivebestaende_CH.xlsx')
#area statistics Standortregionen
areastatistics=sensisto_rcp85.groupby(['storeg','maxsens']).agg({'area_m2': 'sum'})
areastatistics['area_tot_pct']=areastatistics['area_m2']/tot_area*100
areastatistics.to_excel(projectspace+'/areastatistics_rcp85_sensitivebestaende_regionen.xlsx')
#create a pie chart for CH
labels_zahlen = areastatistics_ch.index.get_level_values('maxsens').tolist()
print(labels_zahlen)
print(sensisto_labels)
sizes= areastatistics_ch['area_tot_pct'].tolist()


# Create pie chart for CH RCP8.5 Sensitive Standorte
fig, ax = plt.subplots(figsize=(8, 6))
#ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
# Create pie chart
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=None,  # Remove labels from pie slices
    colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 12},
    pctdistance=0.85,
    counterclock=False)
# Equal aspect ratio
ax.axis('equal')
# Set title
ax.set_title('Klimasensitive Bestände FI RCP8.5 CH', fontsize=14, fontweight='bold',pad=20)
# CREATE CUSTOM LEGEND WITH LABELS
legend_labels = sensisto_labels
ax.legend(
    wedges,
    legend_labels,
    #title="Sensitive Standorte",
    loc="lower right",
    #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
    bbox_to_anchor=(1.2, 0),
    fontsize=9,
    title_fontsize=12,
    frameon=False,
    fancybox=False,
    shadow=False)
plt.tight_layout()
plt.savefig(projectspace+'/areastatistics_rcp85_sensitivebestaende_CH_piechart.png', dpi=300)
plt.show()



# Create pie chart for CH RCP8.5 Sensitive Standorte for each Standortregion
for region in storeg_list:
    print(region)
    tot_area_region=  sensisto_rcp85[sensisto_rcp85['storeg']==region].geometry.area.sum()
    areastatistics_region=sensisto_rcp85[sensisto_rcp85['storeg']==region].groupby(['maxsens']).agg({'area_m2': 'sum'})
    areastatistics_region['area_tot_pct'] = areastatistics_region['area_m2'] / tot_area_region * 100
    #labels_zahlen = areastatistics_region.index.get_level_values('sensisto').tolist()
    print(labels_zahlen)
    print(sensisto_labels)
    #sizes = areastatistics_region['area_tot_pct'].tolist()
    sizes=[]
    for key in labels_zahlen:
        if key in areastatistics_region.index:
            sizes.append(areastatistics_region.loc[key,'area_tot_pct'])
        else:
            sizes.append(0)
    print(sizes)
    fig, ax = plt.subplots(figsize=(8, 6))
    #ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,  # Remove labels from pie slices
        colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12},
        pctdistance=0.85,
        counterclock=False)
    # Equal aspect ratio
    ax.axis('equal')
    # Set title
    ax.set_title('Klimasensitive Bestände FI RCP8.5 Region '+region, fontsize=14, fontweight='bold',pad=20)
    # CREATE CUSTOM LEGEND WITH LABELS
    legend_labels = sensisto_labels
    ax.legend(
        wedges,
        legend_labels,
        #title="Sensitive Standorte",
        loc="lower right",
        #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
        bbox_to_anchor=(1.2, 0),
        fontsize=9,
        title_fontsize=12,
        frameon=False,
        fancybox=False,
        shadow=False)
    plt.tight_layout()
    plt.savefig(projectspace+'/areastatistics_rcp85_sensitivebestaende_piechart_'+region+'.png', dpi=300)
    plt.show()
#delete data
del(sensisto_rcp85)
