# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 16:35:59 2020

@author: sriva
"""
import time
import numpy as np
import pandas as pd
import os

class SpotifyDataExtractor:
    def __init__(self, sp, artist_uri, artist_name, engine):
        self.sp = sp
        self.artist_uri = artist_uri
        self.artist_name = artist_name
        self.conn = engine
        self.sp_albums = self.sp.artist_albums(self.artist_uri, album_type=''
                                                                           '')
        self.album_names = []
        self.album_uris = []
        for i in range(len(self.sp_albums['items'])):
            self.album_names.append(self.sp_albums['items'][i]['name'])
            self.album_uris.append(self.sp_albums['items'][i]['uri'])
           
        self.spotify_albums = {}
        self.album_count = 0
        
    def _extract_album_songs(self, uri):
        album = uri
        self.spotify_albums[album] = {}
        self.spotify_albums[album]['album'] = []
        self.spotify_albums[album]['track_number'] = []
        self.spotify_albums[album]['id'] = []
        self.spotify_albums[album]['name'] = []
        self.spotify_albums[album]['uri'] = []
        
        tracks = self.sp.album_tracks(album)
        
        for i in range(len(tracks['items'])):
            self.spotify_albums[album]['album'].append(self.album_names[self.album_count])
            self.spotify_albums[album]['track_number'].append(tracks['items'][i]['track_number'])
            self.spotify_albums[album]['id'].append(tracks['items'][i]['id'])
            self.spotify_albums[album]['name'].append(tracks['items'][i]['name'])
            self.spotify_albums[album]['uri'].append(tracks['items'][i]['uri'])
            
    def _extract_audio_features(self, album):
        self.spotify_albums[album]['acousticness'] = []
        self.spotify_albums[album]['danceability'] = []
        self.spotify_albums[album]['energy'] = []
        self.spotify_albums[album]['instrumentalness'] = []
        self.spotify_albums[album]['liveness'] = []
        self.spotify_albums[album]['loudness'] = []
        self.spotify_albums[album]['speechiness'] = []
        self.spotify_albums[album]['tempo'] = []
        self.spotify_albums[album]['valence'] = []
        self.spotify_albums[album]['popularity'] = []
        
        track_count = 0
        
        for track in self.spotify_albums[album]['uri']:
            features = self.sp.audio_features(track)
            
            self.spotify_albums[album]['acousticness'].append(features[0]['acousticness'])
            self.spotify_albums[album]['danceability'].append(features[0]['danceability'])
            self.spotify_albums[album]['energy'].append(features[0]['energy'])
            self.spotify_albums[album]['instrumentalness'].append(features[0]['instrumentalness'])
            self.spotify_albums[album]['liveness'].append(features[0]['liveness'])
            self.spotify_albums[album]['loudness'].append(features[0]['loudness'])
            self.spotify_albums[album]['speechiness'].append(features[0]['speechiness'])
            self.spotify_albums[album]['tempo'].append(features[0]['tempo'])
            self.spotify_albums[album]['valence'].append(features[0]['valence'])
            #popularity is stored elsewhere
            pop = self.sp.track(track)
            self.spotify_albums[album]['popularity'].append(pop['popularity'])
            track_count+=1
    
    def build_dataframe(self):
        sleep_min = 2
        sleep_max = 5
        start_time = time.time()
        request_count = 0
        
        for uri in self.album_uris:
            self._extract_album_songs(uri)
            print("Album " + str(self.album_names[self.album_count]) + " songs has been added to spotify_albums dictionary")
            self.album_count+=1
            
        for album in self.spotify_albums:
            self._extract_audio_features(album)
            request_count+=1
            if request_count % 5 == 0:
                print(str(request_count) + " playlists completed")
                time.sleep(np.random.uniform(sleep_min, sleep_max))
                print('Loop #: {}'.format(request_count))
                print('Elapsed Time: {} seconds'.format(time.time() - start_time))
        
        spotify_data_dict = {}
        spotify_data_dict['album'] = []
        spotify_data_dict['track_number'] = []
        spotify_data_dict['id'] = []
        spotify_data_dict['name'] = []
        spotify_data_dict['uri'] = []
        spotify_data_dict['acousticness'] = []
        spotify_data_dict['danceability'] = []
        spotify_data_dict['energy'] = []
        spotify_data_dict['instrumentalness'] = []
        spotify_data_dict['liveness'] = []
        spotify_data_dict['loudness'] = []
        spotify_data_dict['speechiness'] = []
        spotify_data_dict['tempo'] = []
        spotify_data_dict['valence'] = []
        spotify_data_dict['popularity'] = []
        for album in self.spotify_albums: 
            for feature in self.spotify_albums[album]:
                spotify_data_dict[feature].extend(self.spotify_albums[album][feature])
                
        spotify_data = pd.DataFrame(spotify_data_dict)
        spotify_data['artist'] = self.artist_name
        spotify_data = spotify_data.sort_values('popularity', ascending=False).drop_duplicates('name').sort_index()
#         spotify_data.to_csv('{}_data.csv'.format(str(time.time())), index=False)
#         print('Dataframe exported to csv')
        start_time = time.time()
        print('Data transfer to sql table started...')
        genre_df.to_sql('WKR_SPOTIFY_DATA', con=self.conn, if_exists='append', index=False, method='multi', chunksize=100)
        print('Data dumped to the working sql table in {} seconds.'.format(time.time()-start_time))

