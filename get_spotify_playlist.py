import pandas as pd
import spotipy
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials
import json
import os

#Set up Connection
client_id = os.environ.get('spotify_id')
client_secret = os.environ.get('spotify_secret')
username = os.environ.get('spotify_user')
scope = 'playlist-read-private'
redirect_uri='http://google.com/'

token = util.prompt_for_user_token(
    username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

#Create Dataframe of Tracks with columns: Artist(s), TrackName and Album
def dataframe_tracks(tracks):
    """@param tracks: json track lists"""
    track_list_ = []
    artists_ = []
    albums_ = []
    for idx,item in enumerate(tracks['items']):
        track_detail = item['track']
        track_list_.append(track_detail['name'])
        artists_.append(track_detail['artists'][0]['name'])
        albums_.append(track_detail['album']['name'])

    df = pd.DataFrame({'Artist(s)' : pd.Series(artists_),'TrackName' : pd.Series(track_list_), 'Album' : pd.Series(albums_)})
    return(df)

#Get Total Playlist
def get_playlists(playlistname):
    """@param playlistname: specific playlist name"""
    if token:
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username and playlist['name'] == playlistname:
                playlist_name = playlist['name']
                results = sp.user_playlist(username, playlist['id'])
                tracks = results['tracks']
                this_df = dataframe_tracks(tracks)
                over_df = []
                if len(this_df) == 100:
                    while tracks['next']:
                        tracks = sp.next(tracks)
                        this_df_n = dataframe_tracks(tracks)
                        if len(this_df_n) <= 100:
                            over_df.append(this_df_n)
                            continue
                else:
                    continue
        if over_df:
            total_df = pd.concat(over_df)      
            df = pd.concat([this_df,total_df]).reset_index(drop = True)
        else:
            df = this_df
    else:
        print('Retrieving playlist failed...')
    return(df)

your_playlist_df = get_playlists(playlistname = "your playlist")