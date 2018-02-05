
                                                                       OSM Data Wrangling Project Report                                                              
                                                                       Gregor Bricelj

# OpenStreetMap Data Wrangling Project

Version 1.1, 2018 January 31

The goal of this project is to audit the original .osm file, clean several fields in the dataset, convert the changed data into .csv format, insert it into a SQL database, then run some database queries.

## Map Area
Map area used in this project is a custom Southeast Slovenia extract (OSM/XML) from MapZen.com, can be retrieved at:

https://mapzen.com/data/metro-extracts/your-extracts/e5319dfc3f62 or:

https://drive.google.com/file/d/1DTymS-nlkuSDQ0OELXaMwlEhRKA0LHH8/view?usp=sharing
    
For this project I used Python 2, Jupyter Notebook 5, SQLite 3, SQLite Analyzer, LibreOffice 5, and Notepad++.
The chosen map covers the far too often forgotten part of Slovenia that I come from, as well as parts of the neighboring Croatian border regions.

### Problems Encountered in the Map
After running some initial code against it, I realized that the map area is already reasonably clean, or at least somewhat cleaner than I had expected. Still, there were some problems with map data that called for data cleaning - mostly due to user entry errors and data taken from legacy systems and applications:

**1** Inconsistent or erroneous phone numbers with country codes '385' (Croatia) and '386' (Slovenia) (*e. g., "385 51 810 611", "0038673568121", "00386"*)

**2** Inconsistent or erroneous postal codes from both Slovenia and Croatia (*Slovenian postal codes have 4 digits, Croatian have 5 - "51312", "00386", "8343", etc.*)

**3** Inconsistent house number values (*"12/f", "13, 13A", "63 km", etc.*)

**4** Inconsistent descriptions of OSM data sources (*e.g., "Bing lowres", "Bing;GPS", etc.*)

**5** Overabbreviated and inconsistent names of streets, entities and places (*"M. Cikava", "PGD ŠALKA VAS", "51311 Skrad", etc.*)

### Phone and fax numbers
I found out that in the original .osm file, users entered phone and fax numbers in many different formats. Both Slovenian and Croatian phone and fax numbers are present. To deal with all the different possibilities of formatting, I resorted to regular expressions and iteration in combination with a special "valid exceptions" dictionary to read, validate and update the actual numbers. I chose the format *+385X(...)X* or *+386X(...)X* for the updated values:

*"041 290 990"* ==> *"+38641290990"*

*"+386(0)7 393 45 20"* ==> "+38673934520"*

*"+385 91 4971 080"* ==> "+385914971080"*

The SQL database could then be queried. I could, for example, check how many Slovenian (country code +386) and Croatian (+385) valid phone numbers are present in the database:

```sqlite> SELECT substr(all_tags.value, 1, 4), COUNT (*) AS counts
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) all_tags
   ...> WHERE key = 'phone' AND substr(all_tags.value, 1, 4) != ''
   ...> GROUP BY substr(all_tags.value, 1, 4);
```

**Output (condensed): +385|13, +386|68**

### Postal Codes
Postal codes in Slovenia and Croatia are formatted differently. Slovenian postal codes come with 4 digits and Croatian with 5 digits, within ranges that are country-specific. To deal with both postcode formats, I compared any postal code string against 4 short lists of all possible (4- and 5- digit) regional postal codes. This way I was able to also filter out any erroneous entries. (Interestingly, I discovered that that one of the relevant postal numbers (47250 Duga Resa) was not included in my original source of Croatian regional postal codes http://documents.inter-biz.hr/posta.php. I found it after additional search at the official Croatian postal website https://www.posta.hr/pretrazivanje-mjesta-s-pripadajucim-postanskim-brojem/1403?pojam=Karlova%C4%8Dk&page=15. This demonstrates the importance of finding reliable data sources to work with).
A query for the number of times that individual Croatian (for the sake of shorter output) postal codes appear in the database:
```
sqlite> SELECT all_tags.value, COUNT (*) as counts
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) all_tags
   ...> WHERE key = 'postcode' AND all_tags.value != '' AND length(all_tags.value) = 5
   ...> GROUP BY all_tags.value
   ...> ORDER BY counts DESC;
```

**Output:**

**47280|9, 47251|4, 47276|3, 51328|2, 47250|1, 47272|1, 47282|1, 51311|1, 51312|1, 51325|1, 51329|1**

### OSM Data Sources
The .osm map data come from a variety of sources - various Slovenian and U.S. state agencies, individuals and companies. It made sense to aggregate them somewhat, to both remove unneccessary duplication and to make the subsequent SQL queries more useful. To make the aggregation step (using a mapping) more truthful, I had to explore the internet for relevant data. For example, "landsat" is being co-managed by USGS and NASA, and was therefore remapped to "U.S.".

Example mapping: *"Bing lowres", "Bing;GPS", "Bing;survey", "Bing;survey;Internet", "bing"* ==> *"Bing"*
```
sqlite> SELECT all_tags.value, COUNT (*) AS counts
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) all_tags
   ...> WHERE key = 'source'
   ...> GROUP BY all_tags.value
   ...> ORDER BY counts DESC;
```

**Output:**

**RABA-KGZ|29488, GURS|18202, DigitalGlobe|154, Bing|145, MapBox|135, survey|113, GPS|55, U.S.|55, gps-planine.com|52, Yahoo|11, commons.wikimedia.org|2, hydro|2, ourairports.com|2**


```python
from bokeh.io import show, output_file, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label

# correction of visuals:
%config InlineBackend.figure_format = 'retina'

# disable warnings
import warnings
warnings.filterwarnings('ignore')
```


```python
sources = ['RABA-KGZ', 'GURS', 'DigitalGlobe', 'Bing', 'MapBox', 'survey', 'GPS', 'U.S.', \
           'gps-planine.com', 'Yahoo']
counts = [29488, 18202, 154, 145, 135, 113, 55, 55, 52, 11]

#output_file("sources_bars_basic.html")
output_notebook(resources=None, verbose=False, hide_banner=True, load_timeout=5000, notebook_type='jupyter')

plot = figure(x_range=sources, plot_width=900, plot_height=400,
              title="Top 10 OSM Data Sources With Counts", toolbar_location=None, tools="")

plot.vbar(x=sources, top=counts, width=0.9, fill_alpha=0.8)

plot.xgrid.grid_line_color = None
plot.border_fill_color = None
plot.outline_line_color = None
plot.y_range.start = 0

plot.title.align = "center"
plot.title.text_color = "black"
plot.title.text_font_size = "22px"
plot.title.text_alpha = 0.7

show(plot)
```





<div class="bk-root">
    <div class="bk-plotdiv" id="c222575b-6c5b-452d-8e73-a7472ea164aa"></div>
</div>




The great majority of data (sources RABA-KGZ and GURS) in the .osm file seems to come from Slovenian state agencies, which explains why the dataset felt relatively 'clean' already from the start.

### House Number Values
Next, I wrote a script that read house numbers in many different formats and updated them to a more desirable form, using regular expressions and iteration (Python2 code):
```
housenumber_re = re.compile(r'([b]{2})|(\d{1,3}\skm)|(\d{1,3})([a-zA-Z])?[, /-]*([a-zA-Z])?			              (\d{1,3})*([a-zA-Z])*', re.IGNORECASE)

def audit_housenumber(housenumber):
    mo = housenumber_re.search(housenumber)
    if mo:
        try:
            return (mo.group()).upper()
        except AttributeError:
            return ''
    else:
        return ''   

remove_chars = set('/ ')
def housenumberUpdate(housenumber):
    new_housenum = audit_housenumber(housenumber)
    if new_housenum:
        if new_housenum[-3:] == ' km':     
            return new_housenum
        else:
            return (''.join([char for char in new_housenum if char not in remove_chars])).upper()
```

The resulting house numbers were formatted like the following examples: 

*"12/f"* ==> *"12F"*

*"A"* ==> (return empty string)

*"bb"* ==> *"BB"*

*"13, 13A"* ==> *"13,13A"* (several house numbers in one data field, remove space)

*"63 km"* ==> *"63 km"* (no change wanted in this case)

### Names
Due to grammar-related nature of Slovenian and Croatian languages (such as noun cases and various possible positions of Name abbreviations), and character encoding, I decided to use a mix of regular expressions and iteration to correct some 'name' values. For this purpose, I used both a mapping to take care of the most common abbreviations and a special exceptions dictionary for the rest (see *name_update2.py* for code). The resulting update of substrings in problematic 'name' strings results in (e. g.):

*"Sv. Jelena"* ==> *"Sveta Jelena"* (female gender)

*"Sv. Vid"* ==> *"Sveti Vid"* (male gender)

*"Benzinska stanica J. Brod"* ==> *"Benzinska stanica Jurovski Brod"* (abbreviation in the middle of the string)

## Basic Data Overview
Following are some basic statistics about the dataset, starting with a description of the map in terms of time and space (timestamp data, geographic location data).

### Map Data in Time and Space
```
sqlite> SELECT COUNT(substr(timestamps.timestamp, 1, 4)) AS timestamps_yr
   ...> FROM (SELECT timestamp FROM nodes UNION ALL SELECT timestamp FROM ways) AS timestamps
   ...> ORDER BY timestamps_yr;
```
**Output: 1342420**
```
sqlite> SELECT substr(timestamps.timestamp, 1, 4), COUNT(substr(timestamps.timestamp, 1, 4)) AS 	 data_yr
   ...> FROM (SELECT timestamp FROM nodes UNION ALL SELECT timestamp FROM ways) AS timestamps
   ...> GROUP BY substr(timestamps.timestamp, 1, 4);
```
**Output:**

**2007|222, 2008|1232, 2009|4845, 2010|3057, 2011|6619, 2012|16721, 2013|10530, 2014|54247, 2015|307206, 2016|132342, 2017|805399**

What can be seen from the queries above is that the OSM data for this region is quite recent (added either manually or programmatically from some legacy datasets), with 0.8M out of 1.3M timestamps being added just in 2017:


```python
years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']

counts = [222, 1232, 4845, 3057, 6619, 16721, 10530, 54247, 307206, 132342, 805399]

#output_file("timestamps_bars_basic.html")
output_notebook(resources=None, verbose=False, hide_banner=True, load_timeout=5000, notebook_type='jupyter')

plot = figure(x_range=years, plot_width=900, plot_height=400,
              title="OSM Data Records Added by Year", toolbar_location=None, tools="")

plot.vbar(x=years, top=counts, width=0.9, fill_alpha=0.8, color="orange")

plot.xgrid.grid_line_color = None
plot.border_fill_color = None
plot.outline_line_color = None
plot.y_range.start = 0

plot.title.align = "center"
plot.title.text_color = "black"
plot.title.text_font_size = "22px"
plot.title.text_alpha = 0.7

show(plot)
```





<div class="bk-root">
    <div class="bk-plotdiv" id="0aa0ed78-df69-4358-b7d0-1fe6ab23024d"></div>
</div>




Using only SQL queries, I could also make a pretty good estimate of the map location, assuming that extreme latitude and longitude values denote the estimated map borders:
```
sqlite> SELECT max(nodes.lat), min(nodes.lat), max(nodes.lon), min(nodes.lon) FROM nodes;
```
**Output:**

**45.8684963|45.4215904|15.4007719|14.8782348**

**All four resulting values are positive, meaning that the .osm map area lies approximately between 45.8 - 45.4 N and 15.4 - 14.8 E.**

### Database File Size
To get the information on the size of the database file, I used SQLite Analyzer, which can be downloaded from the SQLite website.
```
PS D:\p4_sqlite> .\sqlite3_analyzer p4db.db
```
**Output (≈137MB):**

/** Disk-Space Utilization Report For p4db.db**

**Size of the file in bytes......................... 143664128**

### Number of Nodes and Ways
```
sqlite> SELECT COUNT(*) FROM nodes;
```
**Output: 1277430**
```
sqlite> SELECT COUNT(*) FROM ways;
```
**Output: 64990**

### Number of Unique Users
```
sqlite> SELECT COUNT(DISTINCT(user.uid))
   ...> FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) user;
```   
**Output: 237**

### Land Use in Numbers
There is a nuber of interesting queries that can be made to see where the local people's interests lie. One of them is 'land use' (the query is omitted because it is structured the same as the query under OSM Data Sources, above):

**Output: **

**farmland|6461, meadow|6195, orchard|2703, vineyard|2437, forest|2295, plantation|407, residential|323, greenhouse_horticulture|48, cemetery|46, industrial|20, grass|17, plant_nursery|17, retail|7, farmyard|5, quarry|5, aquaculture|1, basin|1, commercial|1, landfill|1, recreation_ground|1**


```python
land_use = ['farmland', 'meadow', 'orchard', 'vineyard', 'forest', 'plantation', 'residential', \
            'greenhouse', 'cemetery', 'industrial']

counts = [6461, 6195, 2703, 2437, 2295, 407, 323, 48, 46, 20]

#output_file("landUse_bars_basic.html")
output_notebook(resources=None, verbose=False, hide_banner=True, load_timeout=5000, notebook_type='jupyter')

plot = figure(x_range=land_use, plot_width=900, plot_height=400,
              title="Top 10 Land Uses", toolbar_location=None, tools="")

plot.vbar(x=land_use, top=counts, width=0.9, fill_alpha=0.8, color="green")

plot.xgrid.grid_line_color = None
plot.border_fill_color = None
plot.outline_line_color = None
plot.y_range.start = 0

plot.title.align = "center"
plot.title.text_color = "black"
plot.title.text_font_size = "22px"
plot.title.text_alpha = 0.7

show(plot)
```





<div class="bk-root">
    <div class="bk-plotdiv" id="46411691-ada6-47f5-85ee-746564d622ee"></div>
</div>




### Top 5 Sports Facilities
The sports facilities that appear in the database show what sports are popular in the area. Here are the top 5:
```
sqlite> SELECT all_tags.value, COUNT (*) as counts
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) all_tags
   ...> WHERE key = 'sport'
   ...> GROUP BY all_tags.value
   ...> ORDER BY counts DESC
   ...> LIMIT 5;
```
**Output: tennis|16, basketball|8, soccer|8, swimming|3, handball|2**

### Amenities
Finally, here is a list of notable amenities found in the database (with condensed output):
```
sqlite> SELECT all_tags.value
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) all_tags
   ...> WHERE key = 'amenity' AND all_tags.value != 'yes' AND all_tags.value != 'waste_basket'
   ...> GROUP BY all_tags.value;
```
**Output: **

**atm, bank, bar, bench, bicycle_parking, bus_station, cafe, car_rental, car_wash, charging_station, cinema, community_centre, culture_center, doctors, drinking_water, driving_school, fast_food, fire_station, fountain, fuel, grave_yard, hospital, ice_cream, kindergarten, library, marketplace, massage, monastery, nightclub, parking, parking_space, pharmacy, place_of_worship, police, post_office, pub, public_building, recycling, restaurant, school, social_facility, swimming_pool, telephone, theatre, toilets, townhall, vending_machine**

## Additional Ideas
### Amelioration of Data Aging
As seen in Map Data in Time and Space query above, the data in the .osm file seems to be largely up-to-date. I could plug the values from above into a simple Python function to calculate how 'old' the data is on average (assuming that at the time of this writing data from 2017 is about .5 years old, data from 2016 about 1.5 years old, etc.)(Python2 code):
```
timestamp_counts = {'2007':'222', '2008':'1232', '2009':'4845', '2010':'3057', '2011':'6619',
                    '2012':'16721', '2013':'10530', '2014':'54247', '2015':'307206', '2016':'132342',
                    '2017':'805399'}
                   
data_ages = []
num_of_timestamps = 0
for year, count in timestamp_counts.items():
    age_sum = float(2017.5 - int(year)) * int(count)
    data_ages.append(age_sum)
    num_of_timestamps += int(count)
avg_data_age = round((sum(data_ages) / num_of_timestamps), 2)
print avg_data_age
```
**Output: 1.36**

On average, the data in the database appears to be about 1.4 years old. The quality of the data data could be maintained or even improved if there was some system in place which would assist users in keeping the data up-to-date. For this purpose, some additional info about data ‘age’ could be updated automatically using the timestamp values from the database and the system clock. Once the data entries’ timestamps would exceed a certain ‘age’, the system could send a message to the users, prompting them to verify and/or update the relevant data. 

A few of the benefits of such a mechanism would be:

- users could make more informed decisions on whether to use the current database data or not,
- an incentive for users to recheck the validity of data in nature (and spend some time outdoors) while likely also adding new, unrelated, up-to-date data to the database.

The above suggestion comes with many potential issues, some of which are:

- different data entries ‘age’ at different paces, and only select entries should occasionally be updated (in different intervals), while other data hardly ever changes (e. g., ‘postcode’ entries) so there is no need for prompting,
- the system should probably only send a message once a certain amount of timestamp values gets ‘old’, not for every individual timestamp, to avoid incessant prompting and irking of the user,
- if any problem arises with the system clock or timestamps, users could get prompted, or not, when the exact opposite is desired,
- the tables would need to be expanded (new schema) to store additional user contact data, while the user may be inactive or not at all interested in updating the data,
- the rechecked or changed data entries should get new timestamps.

# Conclusion
The data in the database is reasonably clean, and allows for creation of many more interesting statistics about the map area, I only made a few for the purpose of this presentation. It turns out that users input (sometimes erroneous) data into the original .osm file in many different formats. While the user error will always be there, adhering to some conventional data input formats would increase data usability, readability, and allow for simpler SQL queries.
