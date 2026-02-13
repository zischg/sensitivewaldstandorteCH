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
    -999: (110.0/255.0,110.0/255.0,114.0/255.0),  # Keine Angabe, Grau
    1: (30.0/255.0,41.0/255.0,235.0/255.0),      # Empfohlen, Dunkles Blau
    2: (9.0/255.0,132.0/255.0,255.0/255.0),    # Bedingt empfohlen, Helles Blau
    3: (145.0/255.0,82.0/255.0,45.0/255.0),      # Gefährdet, Braun
    4: (248.0/255.0,238.0/255.0,51.0/255.0), # In Zukunft empfohlen, Gelb
    5: (237.0/255.0,171.0/255.0, 100.0/255.0), # In Zukunft bedingt empfohlen, Orange
    6: (239.0/255.0,180.0/255.0, 200.0/255.0)      # Langfristig gefährdet (Arve) rosa
}


#sensisto_labels = ['Kein klimasensitiver Standort', 'Klimasensitiver Standort', 'Langfristig klimasensitiver Standort', 'Teilweise klimasensitiver Standort']
sensisto_labels = ['Keine Angabe', 'Empfohlen', 'Bedingt empfohlen', 'Gefährdet', 'In Zukunft empfohlen','In Zukunft bedingt empfohlen', 'Langfristig gefährdet']#, 'Bedingt klimasensitiv'] Für alle Standorte mit Arven
baumarten_list=['FI','BU', 'WLI','TEI', 'TA']
labels_zahlen = [-999, 1, 2, 3, 4, 5,6]

#input data
codeworkspace="C:/DATA/develops/sensitivewaldstandorteCH"
projectspace="D:/CCW24sensi"
#projectspace="C:/DATA"
climatescenarios=['rcp45','rcp85']
#climatescenario="rcp85"
#climatescenario="rcp45"
#climatescenario="rcp26"

#import data from database
#Baumartenempfehlungen

for climatescenario in climatescenarios:
    sql = 'SELECT * FROM public."'+climatescenario+'_baumartenempfehlungen"'
    ba = gpd.read_postgis(sql, con=engine, geom_col='geom')
    ba.columns
    storeg_list = ba['storeg'].unique().tolist()
    storeg_list.sort()
    print(storeg_list)
    len(ba)
    ba = ba[ba['inanalysis'] == 1]
    len(ba)
    tot_area = ba.geometry.area.sum()
    #tot_area/1000000
    # Area statistics CH
    for baumart in baumarten_list:
        print(baumart)
        areastatistics_ch = ba.groupby([baumart]).agg({'area_m2': 'sum'})
        areastatistics_ch['area_tot_pct'] = areastatistics_ch['area_m2'] / tot_area * 100
        # areastatistics_ch['area_tot_ant']=areastatistics_ch['area_m2']/tot_area
        areastatistics_ch.to_excel(projectspace + '/areastatistics_'+climatescenario+'_Baumartenempfehlungen_'+baumart+'_CH.xlsx')
        # area statistics Standortregionen
        areastatistics = ba.groupby(['storeg', baumart]).agg({'area_m2': 'sum'})
        areastatistics['area_tot_pct'] = areastatistics['area_m2'] / tot_area * 100
        areastatistics.to_excel(projectspace + '/areastatistics_'+climatescenario+'_Baumartenempfehlungen_'+baumart+'_regionen.xlsx')
        # create a pie chart for CH
        labels = areastatistics_ch.index.get_level_values(baumart).tolist()
        print(labels)
        print(labels_zahlen)
        print(sensisto_labels)
        sizes = []
        for key in labels_zahlen:
            if key in areastatistics_ch.index:
                sizes.append(areastatistics_ch.loc[key, 'area_tot_pct'])
            else:
                sizes.append(0)
        #sizes = areastatistics_ch['area_tot_pct'].tolist()
        # Create pie chart for CH Baumartenempfehlung
        fig, ax = plt.subplots(figsize=(6, 4))
        #ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,  # Remove labels from pie slices
            colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
            #autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10},
            #autopct=lambda pct: f'{pct:.1f}%' if pct >= 3 else '',
            autopct=my_autopct,
            pctdistance=0.85,
            counterclock=False)
        # Equal aspect ratio
        ax.axis('equal')
        # Set title
        #ax.set_title('Baumartenempfehlung '+baumart+' '+climatescenario.replace('45','4.5').replace('85','8.5').replace('rcp','RCP')+' CH', fontsize=12, fontweight='bold',loc='center',pad=20)

        # === CENTERED TITLE ===
        fig.suptitle(
            'Baumartenempfehlung ' + baumart + ' ' +
            climatescenario.replace('45', '4.5').replace('85', '8.5').replace('rcp', 'RCP') + ' CH',
            fontsize=12,
            fontweight='bold',
            # y=1.02,  # adjust if needed (1.0–1.05 usually perfect)
            ha='center'
        )

        # CREATE CUSTOM LEGEND WITH LABELS
        # Add labels outside the pie with leader lines
        legend_labels = sensisto_labels
        ax.legend(
            wedges,
            legend_labels,
            #title="Sensitive Standorte",
            #loc="lower right",
            loc="center left",
            #bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
            bbox_to_anchor=(1.0, 0.5),
            fontsize=9,
            title_fontsize=12,
            frameon=False,
            fancybox=False,
            shadow=False)
        plt.tight_layout()
        plt.savefig(projectspace+'/areastatistics_'+climatescenario+'_Baumartenempfehlung_CH_'+baumart+'_piechart.png', dpi=300)
        plt.show()

    # Create pie chart for CH RCP4.5 Sensitive Standorte for each Standortregion
    for region in storeg_list:
        print(region)
        for baumart in baumarten_list:
            print(baumart)
            tot_area_region = ba[ba['storeg'] == region].geometry.area.sum()
            areastatistics_region = ba[ba['storeg'] == region].groupby([baumart]).agg({'area_m2': 'sum'})
            areastatistics_region['area_tot_pct'] = areastatistics_region['area_m2'] / tot_area_region * 100
            # create a pie chart for CH
            labels = areastatistics_region.index.get_level_values(baumart).tolist()
            #print(labels)
            #print(labels_zahlen)
            #print(sensisto_labels)
            sizes = []
            for key in labels_zahlen:
                if key in areastatistics_region.index:
                    sizes.append(areastatistics_region.loc[key, 'area_tot_pct'])
                else:
                    sizes.append(0)
            # sizes = areastatistics_region['area_tot_pct'].tolist()
            # Create pie chart for CH Baumartenempfehlung
            fig, ax = plt.subplots(figsize=(6, 4))
            # ax.pie(sizes, labels=sensisto_labels, autopct='%1.1f%%', colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()], startangle=90, textprops={'size': 'smaller'}, counterclock=False)
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=None,  # Remove labels from pie slices
                colors=[sensisto_colors_dict[key] for key in sensisto_colors_dict.keys()],
                #autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10},
                autopct=my_autopct,
                pctdistance=0.85,
                counterclock=False)
            # Equal aspect ratio
            ax.axis('equal')
            # Set title
            #ax.set_title('Baumartenempfehlung ' + baumart + ' ' + climatescenario.replace('45', '4.5').replace('85', '8.5').replace('rcp', 'RCP') + ' Region '+region, fontsize=12, fontweight='bold', loc='center',pad=20)

            # === CENTERED TITLE ===
            fig.suptitle(
                'Baumartenempfehlung ' + baumart + ' ' +
                climatescenario.replace('45', '4.5').replace('85', '8.5').replace('rcp', 'RCP') + ' Region '+region,
                fontsize=12,
                fontweight='bold',
                #y=1.02,  # adjust if needed (1.0–1.05 usually perfect)
                ha='center'
            )

            # CREATE CUSTOM LEGEND WITH LABELS
            legend_labels = sensisto_labels
            ax.legend(
                wedges,
                legend_labels,
                # title="Sensitive Standorte",
                loc="center left",
                # bbox_to_anchor=(1, 0, 0.5, 1),  # Position outside plot
                bbox_to_anchor=(1.0, 0.5),
                fontsize=9,
                title_fontsize=12,
                frameon=False,
                fancybox=False,
                shadow=False)
            plt.tight_layout()
            plt.savefig(projectspace + '/areastatistics_' + climatescenario + '_Baumartenempfehlung_CH_' + baumart + '_'+region+'_piechart.png', dpi=300)
            plt.show()
print('all done')






