## P4: OpenStreetMap Data Wrangling Project

Originally created using Python 2, Jupyter Notebook 5, Notepad++ 7, SQLite 3, SQLite Analyzer and LibreOffice 5.

The goal of this project is to audit the original .osm file, clean several fields in the dataset, convert the changed data into .csv format, insert it into a SQL database, then run some database queries.

For results and conclusion, see REPORT.md or REPORT.ipynb file.

Map area used in this project is a custom Southeast Slovenia extract (OSM/XML) from MapZen.com
The chosen OSM map covers Southeastern Slovenia and the neighboring Croatian border region.

Links to map:
- [https://mapzen.com/data/metro-extracts/your-extracts/e5319dfc3f62)
- [https://drive.google.com/file/d/1DTymS-nlkuSDQ0OELXaMwlEhRKA0LHH8/view?usp=sharing)



### Dependencies:

Cerberus ('pip install Cerberus')



### Scripts:

write_to_CSV.py  (main)

schema.py  (describes schema used to translate .csv into SQLite .db)

(the following scripts audit and update select datafields:)
housenumber_update2.py
import phone_update2.py
import email_update2.py
import source_update2.py
import postcode_update2.py
