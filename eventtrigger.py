# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 16:04:33 2020

@author: sriva
"""
import os
from dotenv import load_dotenv
import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotifydataextractor import SpotifyDataExtractor
import pyodbc

logging.basicConfig(level='DEBUG', filename='project_logs.log')

project_folder = os.path.expanduser(r'C:\Users\sriva\OneDrive\Desktop\edu.usf.sas.pal.muser\SpotifyDataExtractor')
load_dotenv(os.path.join(project_folder, '.env'))

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
SERVER = os.environ.get('SERVER')
DATABASE = os.environ.get('DATABASE')

client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
# token = util.prompt_for_user_token(USERNAME, SCOPE, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

try:
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=DESKTOP-NMKR71N;'
                          'Database=muser;'
                          'Trusted_Connection=yes;')
    print(conn)
    cur = conn.cursor()
    
except:
    print('Connection failed...')
    
def main():
    try:
        genre = input('Enter genre: ')
        genre_data = sp.search(genre)
        artist_uri_list = []
        for i in range(len(genre_data['tracks']['items'])):
            for j in range(len(genre_data['tracks']['items'][i]['artists'])):
                artist_uri_list.append(genre_data['tracks']['items'][i]['artists'][j]['uri'])    
        print('{} uris found for the {} genre'.format(len(artist_uri_list), genre))
        for uri in artist_uri_list:
            extractor = SpotifyDataExtractor(sp, uri, cur)
            extractor.build_dataframe()
        print('Data extraction complete for the genre {}.'.format(genre))
        conn.commit()
        cur.close()
    except:
        print('An error occured....')

if __name__ == '__main__':
    main()