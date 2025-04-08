# sensitivewaldstandorteCH
Sensitive Waldstandorte und Bestände Schweiz

Dieses Code Repository dokumentiert die Arbeiten zur Entwicklung einer Karte der Baumartenempfehlungen im Klimawandel, einer Karte zu den klimasensitiven Waldstandorten und einer Karte zu den klimasensitiven Bestände.
Die Methode folgt der Prozedur von Tree-App (https://www.tree-app.ch) und wird mit folgenden Schritten umgesetzt:

1. Extraktion aller Waldstandortstypen einer kantonalen Waldstandortskarte und Ableitung einer Tabelle zu allen kartierten Standortstypen (script XX_hoehenstufen_preprocessing.py mit output XX_nais_einheiten_unique.xlsx, XX_ steht für das Kantonskürzel)
2. Alle kantonalen Standortstypen werden in einen NaiS-Standort übersetzt. Dies erfolgt gutachterlich durch M. Frehner und B. Huber (output XX_nais_einheiten_unique_mf.xlsx)
3. Die Tabelle mit den Übersetzungen und Höhenstufenzuweisungen wird mit der kantonalen Standortskarte verknüpft (script XX_hoehenstufen.py). Output ist eine Waldstandortskarte mit den kantonalen EInheiten, den NaiS-Einheiten und zugeweisenen Höhenstufen.
4. Die übersetzte und harmonisierte Karte der Waldstandortstypen wird mit verschiednen Attributen angereichert (Muldenlagen, Hanglagen, Ebenen, Sonnen- und Schattenhänge, Neigung, Standortsregion, Tannenareal), die es zur Berechnung der Projektionswege braucht. Anschliessend wird folgendes berechnet (script X_sensi_treeapp.py):
  -Die zukünftige Höhenstufe wird für jedes Klimaszenario durch räumliche Überlagerung bestimmt,
  -der zukünftige Standortstyp wird auf Basis der Projektionswegetabelle von NaiS (L_Projektionswege_im_Klimawandel_18022020_export.xlsx) und dem zukünftigen Standortstyp berechnet,
  -der Vergleich der Baumartenzusammensetzung des heutigen und zukünftigen Waldstandorstyps ergibt die Karte der BAumartenempfehlungen (NaiS-MAtrix Baumartentabelle Matrix_Baum_inkl_collin_20210412_mit AbkuerzungenCLEAN.xlsx)
  -auf Basis der Baumartenempfehlungen werden die klimasensitiven Standorte berechnet
5. Die beiden Klimaszenarien RCP4.5 und RCP8.5 werden miteinander kombiniert (script XX_sensi_treeappCombiRCP45RCP85.py)
6. Die sensitiven Bestände werden berechnet (script XX_sensitiveBestaende.py)
