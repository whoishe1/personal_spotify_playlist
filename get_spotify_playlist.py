import pandas as pd
import spotipy
from spotipy import util
import json
import os

class ReturnPlaylist:
    def __init__(self,username,scope,client_id,client_secret,redirect_uri):
        self.username = username 
        self.scope = scope
        self.client_id = client_id 
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_token(self):
        """
        Set credentials 
        """
        token = (util.prompt_for_user_token(
            self.username,
            self.scope,
            self.client_id,
            self.client_secret,
            self.redirect_uri))
        return token

    def dataframe_tracks(self,tracks):
        """
        Helper function get tracklists

        @param tracks: json track lists
        """
        track_list_ = []
        artists_ = []
        albums_ = []
        for idx,item in enumerate(tracks['items']):
            track_detail = item['track']
            track_list_.append(track_detail['name'])
            artists_.append(track_detail['artists'][0]['name'])
            albums_.append(track_detail['album']['name'])

        df = (pd.DataFrame({'Artist(s)' : pd.Series(artists_),
                'TrackName' : pd.Series(track_list_), 
                'Album' : pd.Series(albums_)}))

        return df

    def get_playlists(self,playlistname):
        """
        Retrieve a playlist and return in pandas dataframe format

        @param playlistname: specific playlist name
        """
        try:
            token = self.get_token()
            sp = spotipy.Spotify(auth = token)
            playlists = sp.user_playlists(self.username)
            for playlist in playlists['items']:
                if playlist['owner']['id'] == self.username and playlist['name'] == playlistname:
                    results = sp.user_playlist(self.username, playlist['id'])
                    tracks = results['tracks']
                    this_df = self.dataframe_tracks(tracks)
                    over_df = []
                    if len(this_df) == 100:
                        while tracks['next']:
                            tracks = sp.next(tracks)
                            this_df_n = self.dataframe_tracks(tracks)
                            if len(this_df_n) <= 100:
                                over_df.append(this_df_n)
                                continue
                    else:
                        continue
            if over_df:
                total_df = pd.concat(over_df)      
                pl_df = pd.concat([this_df,total_df]).reset_index(drop = True)
            else:
                pl_df = this_df

        except Exception as e:
            print("Failed to get playlist dataframe because of " + str(e))       

        return pl_df


class MyPlaylists(ReturnPlaylist):
    def __init__(self,username,scope,client_id,client_secret,redirect_uri):
        super(MyPlaylists,self).__init__(username,scope,client_id,client_secret,redirect_uri)

    def my_playlist(self):
        """get all playlist names"""
        try:
            token = self.get_token()
            sp = spotipy.Spotify(auth = token)
            playlists = sp.user_playlists(self.username)            
            stored_playlists = [value for idx,value in enumerate(playlists['items'])]
            list_playlists = [i['name'] for i in stored_playlists]
        
        except Except as e:
            print("Failed to get playlist names because of " + str(e))

        return list_playlists

