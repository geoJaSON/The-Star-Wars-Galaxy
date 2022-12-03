from arcgis import GIS
import pandas as pd
gis = GIS()
layer_item = gis.content.get('530a2b7f92c44ce8b5fd47d2b2e08f5d')
layers = layer_item.layers
flayer = layers[0]
fset = flayer.query()
sdf = pd.DataFrame.spatial.from_layer(flayer)
import re
#%%
for index, row in sdf.head().iterrows():
    plan_dict = {}
    planet = row['name'].replace(" ","_")
    page_url=f"https://starwars.fandom.com/wiki/{planet}/Legends"
    try:
        print(page_url)
        result = requests.get(page_url)
        content = result.content
        soup = BeautifulSoup(content, "html.parser")

        raw_content = soup.find('div', class_='mw-parser-output')
        if raw_content is not None:
            for raw_paragraph in raw_content.find_all('p', recursive=False):
                if 'aside' in str(raw_paragraph): continue
                break
            paragraph = value = re.sub("[\(\[].*?[\)\]]" ,'', raw_paragraph.text)
            print(paragraph)
        else:
            page_url = page_url.replace('/Legends','')
            result = requests.get(page_url)
            content = result.content
            soup = BeautifulSoup(content, "html.parser")
            raw_content = soup.find('div', class_='mw-parser-output')
            if raw_content is not None:
                for raw_paragraph in raw_content.find_all('p', recursive=False):
                    if 'aside' in str(raw_paragraph): continue
                    break
                paragraph = value = re.sub("[\(\[].*?[\)\]]" ,'', raw_paragraph.text)
                print(paragraph)
            else:
                pass
    except:
        pass

side_bar = {}
sec = soup.find_all('section', class_='pi-item')
for s in sec:
    title = s.find('h2')
    if title is None:
        title = '<no category>'
    else:
        title = title.text
    side_bar[title] = {}
    items = s.find_all('div', class_='pi-item')
    for item in items:
        attr = item.find('h3', class_='pi-data-label')
        if attr is None:
            attr = '<no attribute>'
        else:
            attr = attr.text
        value = re.sub("[\(\[].*?[\)\]]" ,'', '], '.join(item.find('div', class_='pi-data-value').text.split(']')))
        print(attr,value)










point_df = df[df.Geometry.isin(['Point'])]
line_df = df[df.Geometry.isin(['Line'])]
poly_df = df[df.Geometry.isin(['Polygon'])]

point_df['Lat'] = point_df['Coordinates'].apply(lambda x :x[0][0]) #convert m numbers to symbols
point_df['Long'] = point_df['Coordinates'].apply(lambda x :x[0][1]) #convert m numbers to symbols
point_df = pd.DataFrame.spatial.from_xy(df=point_df, x_column='Long', y_column='Lat', sr=4326)

poly_features = []
for index, row in poly_df.iterrows():
    shape = {
     "rings": [row['Coordinates']],
     "spatialreference" : {"wkid" : 4326}}
    polygonFeature = geometry.Polygon(shape)
    polygon_new = Feature(geometry=polygonFeature, attributes={"Area": row['Area'],
                                                "Subarea": row['Subarea'],
                                                'LNM':row['LNM'],
                                                'Location Type':row['Location Type'],
                                                'Coordinates':row['Coordinates'],
                                                'Mile Marker':row['Mile Marker'],
                                                'Dates':row['Dates'],
                                                'Max Date':row['Max Date'],
                                                'Summary':row['Summary']})
    poly_features.append(polygon_new)
poly_df = FeatureSet(features = poly_features, geometry_type="Polygon", spatial_reference={'latestWkid': 4326, 'wkid': 102100}).sdf

line_features = []
for index, row in line_df.iterrows():
    shape = {
     "paths": [row['Coordinates']],
     "spatialreference" : {"wkid" : 4326}}
    lineFeature = geometry.Polyline(shape)
    line_new = Feature(geometry=lineFeature, attributes={"Area": row['Area'],
                                                "Subarea": row['Subarea'],
                                                'LNM':row['LNM'],
                                                'Location Type':row['Location Type'],
                                                'Coordinates':row['Coordinates'],
                                                'Mile Marker':row['Mile Marker'],
                                                'Dates':row['Dates'],
                                                'Max Date':row['Max Date'],
                                                'Summary':row['Summary']})
    line_features.append(line_new)
line_df = FeatureSet(features = line_features, geometry_type="Polyline", spatial_reference={'latestWkid': 4326, 'wkid': 102100}).sdf
point_df = point_df.rename({'Area':'area','Subarea':'subarea','LNM':'lnm','Geometry':'derived_geometry','Lat':'latitude','long':'longitude','Location Type':'geolocation_type','Coordinates':'coordinates_list','Mile Marker':'mile_markers_list','Dates':'dates_list','Max Date':'max_date','Summary':'summary'}, axis=1)
line_df = line_df.rename({'Area':'area','Subarea':'subarea','LNM':'lnm','Geometry':'derived_geometry','Lat':'latitude','long':'longitude','Location Type':'geolocation_type','Coordinates':'coordinates_list','Mile Marker':'mile_markers_list','Dates':'dates_list','Max Date':'max_date','Summary':'summary'}, axis=1)
poly_df = poly_df.rename({'Area':'area','Subarea':'subarea','LNM':'lnm','Geometry':'derived_geometry','Lat':'latitude','long':'longitude','Location Type':'geolocation_type','Coordinates':'coordinates_list','Mile Marker':'mile_markers_list','Dates':'dates_list','Max Date':'max_date','Summary':'summary'}, axis=1)


t

point_df['SHAPE']
print(point_df.at[0,'SHAPE'])
