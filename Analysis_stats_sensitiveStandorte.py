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
db_connection_url = "postgresql://";
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

def my_autopct(pct):
    return ('%1.1f%%' % pct) if pct >= 2 else ''   # only show ≥ 4%


#color dictionaries
# Define specific RGB colors for each class combination (normalized to [0,1])
sensisto_colors_dict = {
    0: (30.0/255.0,41.0/255.0,235.0/255.0),      # Kein klimasensitiver Standort, Dunkles Blau
    2: (145.0/255.0,82.0/255.0,45.0/255.0),    # Klimasensitiver Standort, Braun
    3: (239.0/255.0,180.0/255.0, 200.0/255.0),       # Langfristig klimasensitiver Standort, Rosarot
    4: (248.0/255.0,238.0/255.0,51.0/255.0)}      # Teilweise klimasensitiver Standort, Gelb

sensisto_labels = ['Kein klimasensitiver Standort', 'Klimasensitiver Standort', 'Langfristig klimasensitiver Standort', 'Teilweise klimasensitiver Standort']

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
sql='SELECT * FROM public.rcp45_sensitivestandorte'
sensisto_rcp45=gpd.read_postgis(sql, con=engine, geom_col='geom')
sensisto_rcp45.columns
storeg_list=sensisto_rcp45['storeg'].unique().tolist()
storeg_list.sort()
print(storeg_list)
len(sensisto_rcp45)
sensisto_rcp45=sensisto_rcp45[sensisto_rcp45['inanalysis']==1]
len(sensisto_rcp45)
tot_area=  sensisto_rcp45.geometry.area.sum()
tot_areakm2=tot_area/1000000  #convert to km2
# Area statistics CH
areastatistics_ch=sensisto_rcp45.groupby(['sensisto']).agg({'area_m2': 'sum'})
areastatistics_ch['area_tot_pct']=areastatistics_ch['area_m2']/tot_area*100
#areastatistics_ch['area_tot_ant']=areastatistics_ch['area_m2']/tot_area
areastatistics_ch.to_excel(projectspace+'/areastatistics_rcp45_sensitivestandorte_CH.xlsx')
#area statistics Standortregionen
areastatistics=sensisto_rcp45.groupby(['storeg','sensisto']).agg({'area_m2': 'sum'})
areastatistics['area_tot_pct']=areastatistics['area_m2']/tot_area*100
areastatistics.to_excel(projectspace+'/areastatistics_rcp45_sensitivestandorte_regionen.xlsx')
#create a pie chart for CH
labels_zahlen = areastatistics_ch.index.get_level_values('sensisto').tolist()
print(labels_zahlen)
print(sensisto_labels)
sizes= areastatistics_ch['area_tot_pct'].tolist()


# Create pie chart for CH RCP4.5 Sensitive Standorte
fig, ax = plt.subplots(figsize=(6, 4))
#ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
# Create pie chart
wedges, texts, autotexts = ax.pie(
    sizes,
    labels=None,  # Remove labels from pie slices
    colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
    #autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 10, 'fontweight': 'bold'},
    autopct=my_autopct,
    pctdistance=0.85,
    counterclock=False)
# Equal aspect ratio
ax.axis('equal')
# Set title
#ax.set_title('Klimasensitive Standorte RCP4.5 CH', fontsize=12, fontweight='bold',pad=20)

# === CENTERED TITLE ===
fig.suptitle('Klimasensitive Standorte RCP4.5 CH',fontsize=12,fontweight='bold',ha='center')

# CREATE CUSTOM LEGEND WITH LABELS
legend_labels = sensisto_labels
ax.legend(
    wedges,
    legend_labels,
    #title="Sensitive Standorte",
    loc="lower left",
    #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
    bbox_to_anchor=(0.85, 0.0),
    fontsize=9,
    title_fontsize=12,
    frameon=False,
    fancybox=False,
    shadow=False)
plt.tight_layout()
plt.savefig(projectspace+'/areastatistics_rcp45_sensitivestandorte_CH_piechart.png', dpi=300)
plt.show()

# Create pie chart for CH RCP4.5 Sensitive Standorte for each Standortregion
for region in storeg_list:
    print(region)
    tot_area_region=  sensisto_rcp45[sensisto_rcp45['storeg']==region].geometry.area.sum()
    areastatistics_region=sensisto_rcp45[sensisto_rcp45['storeg']==region].groupby(['sensisto']).agg({'area_m2': 'sum'})
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
    fig, ax = plt.subplots(figsize=(6, 4))
    #ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,  # Remove labels from pie slices
        colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
        #autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10, 'fontweight': 'bold'},
        autopct=my_autopct,
        pctdistance=0.85,
        counterclock=False)
    # Equal aspect ratio
    ax.axis('equal')
    # Set title
    #ax.set_title('Klimasensitive Standorte RCP4.5 Region '+region, fontsize=12, fontweight='bold',pad=20)

    # === CENTERED TITLE ===
    fig.suptitle(
        'Klimasensitive Standorte RCP4.5 Region '+region,
        fontsize=12,
        fontweight='bold',
        # y=1.02,  # adjust if needed (1.0–1.05 usually perfect)
        ha='center'
    )

    # CREATE CUSTOM LEGEND WITH LABELS
    legend_labels = sensisto_labels
    ax.legend(
        wedges,
        legend_labels,
        #title="Sensitive Standorte",
        loc="lower left",
        #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
        bbox_to_anchor=(0.85, 0.0),
        fontsize=9,
        title_fontsize=12,
        frameon=False,
        fancybox=False,
        shadow=False)
    plt.tight_layout()
    plt.savefig(projectspace+'/areastatistics_rcp45_sensitivestandorte_piechart_'+region+'.png', dpi=300)
    plt.show()
#delete data
del(sensisto_rcp45)


#rcp85
sql='SELECT * FROM public.rcp85_sensitivestandorte'
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
areastatistics_ch85=sensisto_rcp85.groupby(['sensisto']).agg({'area_m2': 'sum'})
areastatistics_ch85['area_tot_pct']=areastatistics_ch85['area_m2']/tot_area*100
#areastatistics_ch['area_tot_ant']=areastatistics_ch85['area_m2']/tot_area
areastatistics_ch85.to_excel(projectspace+'/areastatistics_rcp85_sensitivestandorte_CH.xlsx')
#area statistics Standortregionen
areastatistics85=sensisto_rcp85.groupby(['storeg','sensisto']).agg({'area_m2': 'sum'})
areastatistics85['area_tot_pct']=areastatistics85['area_m2']/tot_area*100
areastatistics85.to_excel(projectspace+'/areastatistics_rcp85_sensitivestandorte_regionen.xlsx')
#create a pie chart for CH
#labels_zahlen85 = areastatistics_ch85.index.get_level_values('sensisto').tolist()
print(labels_zahlen)
print(sensisto_labels)
sizes85= areastatistics_ch85['area_tot_pct'].tolist()
# Create pie chart for CH RCP8.5 Sensitive Standorte
fig, ax = plt.subplots(figsize=(6, 4))
#ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
# Create pie chart
wedges, texts, autotexts = ax.pie(
    sizes85,
    labels=None,  # Remove labels from pie slices
    colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
    #autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 10, 'fontweight': 'bold'},
    autopct=my_autopct,
    pctdistance=0.85,
    counterclock=False)
# Equal aspect ratio
ax.axis('equal')
# Set title
#ax.set_title('Klimasensitive Standorte RCP8.5 CH', fontsize=14, fontweight='bold',pad=20)
fig.suptitle('Klimasensitive Standorte RCP8.5 CH',fontsize=12,fontweight='bold',ha='center')
# CREATE CUSTOM LEGEND WITH LABELS
legend_labels = sensisto_labels
ax.legend(
    wedges,
    legend_labels,
    #title="Sensitive Standorte",
    loc="lower left",
    # bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
    bbox_to_anchor=(0.85, 0.0),
    fontsize=9,
    title_fontsize=12,
    frameon=False,
    fancybox=False,
    shadow=False)
plt.tight_layout()
plt.savefig(projectspace+'/areastatistics_rcp85_sensitivestandorte_CH_piechart.png', dpi=300)
plt.show()


# Create pie chart for CH RCP8.5 Sensitive Standorte for each Standortregion
for region in storeg_list:
    print(region)
    tot_area_region=  sensisto_rcp85[sensisto_rcp85['storeg']==region].geometry.area.sum()
    areastatistics_region=sensisto_rcp85[sensisto_rcp85['storeg']==region].groupby(['sensisto']).agg({'area_m2': 'sum'})
    areastatistics_region['area_tot_pct'] = areastatistics_region['area_m2'] / tot_area_region * 100
    #labels_zahlen = areastatistics_ch85.index.get_level_values('sensisto').tolist()
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
    fig, ax = plt.subplots(figsize=(6, 4))
    #ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,  # Remove labels from pie slices
        colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
        #autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10, 'fontweight': 'bold'},
        autopct=my_autopct,
        pctdistance=0.85,
        counterclock=False)
    # Equal aspect ratio
    ax.axis('equal')
    # Set title
    #ax.set_title('Klimasensitive Standorte RCP8.5 Region '+region, fontsize=14, fontweight='bold',pad=20)
    fig.suptitle('Klimasensitive Standorte RCP8.5 Region '+region, fontsize=12, fontweight='bold', ha='center')
    # CREATE CUSTOM LEGEND WITH LABELS
    legend_labels = sensisto_labels
    ax.legend(
        wedges,
        legend_labels,
        #title="Sensitive Standorte",
        loc="lower left",
        # bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
        bbox_to_anchor=(0.85, 0.0),
        fontsize=9,
        title_fontsize=12,
        frameon=False,
        fancybox=False,
        shadow=False)
    plt.tight_layout()
    plt.savefig(projectspace+'/areastatistics_rcp85_sensitivestandorte_piechart_'+region+'.png', dpi=300)
    plt.show()
del(sensisto_rcp85)


















# Create a 3x3 grid of pie charts
fig, axes = plt.subplots(3, 3, figsize=(15, 15))
# Plot each pie chart
x=
axes[0,0].pie([1], labels=sensisto_labels, colors=['lightgrey'], startangle=90)



for i, (ax, dataset) in enumerate(zip(axes, data)):
    # Extract labels and values
    labels = list(dataset.keys())
    sizes = list(dataset.values())

    # Get colors for the current dataset
    colors = [colors_dict[label] for label in labels]

    # Create pie chart
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)

    # Equal aspect ratio ensures pie is a circle
    ax.axis('equal')

    # Add title for each pie chart
    ax.set_title(f'Combination {i + 1}', pad=20)

# Create a separate legend for all class combinations
handles = [plt.Rectangle((0, 0), 1, 1, color=colors_dict[label]) for label in colors_dict]
plt.legend(handles, colors_dict.keys(), title="Class Combinations",
           loc="center left", bbox_to_anchor=(1, 0.5), fontsize=10)

# Adjust layout to prevent overlap
plt.tight_layout()

# Show plot
plt.show()




sql='SELECT * FROM public.rcp45_sensitivestandorte'
sensisto_rcp85=gpd.read_postgis(sql, con=engine, geom_col='geom')



combi_unique=combi_unique[combi_unique['tahs_1'].isin(['obersubalpin','subalpin','hochmontan','obermontan','untermontan','submontan','collin'])]
combi_unique=combi_unique.sort_values(by=['nais_1'])
combi_unique.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique.xlsx")

areastatistics=combi.groupby(['nais_1', 'tahs_1', 'tahsue_1', 'nais1_rcp45', 'nais2_rcp45','hs_rcp45', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85']).agg({'area': 'sum'})
areastatistics.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_area.xlsx")

#Einzeln
rcp45.columns
rcp45['area']=rcp45.geometry.area
rcp45=rcp45[rcp45['area']>=100]
rcp45unique=rcp45[['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45', 'mo', 'ue','taheute', 'storeg',]]
rcp45unique=rcp45unique.drop_duplicates()
rcp45unique.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_RCP45.xlsx")
areastatistics_rcp45=rcp45.groupby(['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp45', 'nais2_rcp45', 'hs_rcp45', 'mo', 'ue','taheute', 'storeg']).agg({'area': 'sum'})
areastatistics_rcp45.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_area_RCP45.xlsx")

rcp85.columns
rcp85['area']=rcp85.geometry.area
rcp85=rcp85[rcp85['area']>=100]
rcp85unique=rcp85[['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85', 'mo', 'ue','taheute', 'storeg',]]
rcp85unique=rcp85unique.drop_duplicates()
rcp85unique.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_RCP85.xlsx")
areastatistics_rcp85=rcp85.groupby(['nais', 'nais1', 'nais2','tahs', 'tahsue', 'nais1_rcp85', 'nais2_rcp85', 'hs_rcp85', 'mo', 'ue','taheute', 'storeg']).agg({'area': 'sum'})
areastatistics_rcp85.to_excel(projectspace+'/UR/'+"/UR_Projektionspfade_unique_area_RCP85.xlsx")
print('all done')



for climatescenario in climatescenarios:
    print(climatescenario)

