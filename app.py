from flask import Flask,request, url_for, redirect, render_template
app = Flask(__name__)

import os
import logging
import pandas as pd
from ConnectionManager import ConnectionManager
from spotifydataharvester import SpotifyDataHarvester
from ETL import ETL

os.chdir(r'C:\Users\sriva\OneDrive\Desktop\MusicDataExtractor')
logging.basicConfig(level='DEBUG', filename='project_logs.log')

connection_manager = ConnectionManager()
sp = connection_manager.spotify_connection()
engine = connection_manager.database_connection()

raw_file = pd.read_csv('sample_music_data.csv')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/extract',methods=['POST','GET'])
def extract():
    try:
        input_query = request.form
        input_query = input_query['query']
        spotify_data = sp.search(input_query)
        artist_list = {}
        for i in range(len(spotify_data['tracks']['items'])):
            for j in range(len(spotify_data['tracks']['items'][i]['artists'])):
                artist_list[spotify_data['tracks']['items'][i]['artists'][j]['uri']] = spotify_data['tracks']['items'][i]['artists'][j]['name']
        print('{} uris found for the {} genre'.format(len(artist_list), input_query))
        for uri, name in artist_list.items():
            extractor = SpotifyDataHarvester(sp, uri, name, engine)
            extractor.dump_raw_data()
        print('Data extraction completed for the genre {}.'.format(input_query))
        etl = ETL(engine)
        etl.build_final_table()
        print('Final table ready for analysis')
        return render_template('index.html', msg='Harvest completed')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    app.run()
