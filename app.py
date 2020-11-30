from flask import Flask,request, url_for, redirect, render_template
app = Flask(__name__)

import os
import time
import logging
import pandas as pd
from ConnectionManager import ConnectionManager
from spotifydataextractor import SpotifyDataExtractor
from ETL import ETL

os.chdir(r'C:\Users\sriva\Desktop\edu.usf.sas.pal.muser\SpotifyDataExtractor')
logging.basicConfig(level='DEBUG', filename='project_logs.log')

connection_manager = ConnectionManager()
sp = connection_manager.spotify_connection()
engine = connection_manager.database_connection()

raw_file = pd.read_csv('sample_music_data.csv')

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/extract',methods=['POST','GET'])
def extract():
    try:
        input_query = request.form
        print(input_query)
        genre = input_query['genre']
        genre_data = sp.search(genre)
        artist_list = {}

        for i in range(len(genre_data['tracks']['items'])):
            for j in range(len(genre_data['tracks']['items'][i]['artists'])):
                artist_list[genre_data['tracks']['items'][i]['artists'][j]['uri']] = genre_data['tracks']['items'][i]['artists'][j]['name']
        print('{} uris found for the {} genre'.format(len(artist_list), genre))
        for uri, name in artist_list.items():
            extractor = SpotifyDataExtractor(sp, uri, name, engine)
            extractor.build_dataframe()
        print('Data extraction completed for the genre {}.'.format(genre))
        etl = ETL(engine)
        etl.build_final_table()
        print('Final table ready for analysis')
        return render_template('index.html', msg='Extraction completed' )
    except:
        print('An error occured...')

if __name__ == '__main__':
    app.run()
