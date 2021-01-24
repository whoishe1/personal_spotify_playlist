import pandas as pd
import spotipy
import datetime
import json
import os


class ReturnPlaylist:
    """Returns Tracks, Artists, and Album of a specified playlists in a pandas/xlsx format
    
    Attributes:
        username: Spotify username
        scope: Spotify authorization scopes, i.e. 'playlist-read-private'
        client_id: Spotify client id
        client_secret: Spotify client secret
        redirect_url: redirect authorization url 

    """

    def __init__(self,username,scope,client_id,client_secret,redirect_uri):
        """Initialize ReturnPlayList"""
        self.username = username 
        self.scope = scope
        self.client_id = client_id 
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_token(self):
        """Set credentials """
        token = (spotipy.util.prompt_for_user_token(
            self.username,
            self.scope,
            self.client_id,
            self.client_secret,
            self.redirect_uri))
        return token

    def dataframe_tracks(self,tracks):
        """ Helper function that retrieves the tracklist in a json format for the specified playlist and outputs it into a pandas dataframe.  Only outputs artists, trackname and album.
            
            Arguments:
                tracks: JSON format of specified playlist.

            Returns:
                df: pandas dataframe of specified playlist

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
        Concats playlist into a dataframe.  Spotify has a limit of 100 tracks with their GET request.

            Args:
                playlistname: specific playlist name
            
            Returns:
                pl_df: pandas dataframe of specified playlist
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
        
        except Exception as e:
            print("Failed to get playlist names because of " + str(e))

        return list_playlists


#Example

# username = os.environ.get('spotify_user')
# scope =  'playlist-read-private'
# client_id = os.environ.get('spotify_id')
# client_secret = os.environ.get('spotify_secret')
# redirect_uri = 'https://www.google.com'

# jordans_playlist = MyPlaylists(username,scope,client_id,client_secret,redirect_uri)
# jordans_playlist.my_playlist()

# subset_pl = ['the five','the three','the two','the one']

# ret_jordans_pl = ReturnPlaylist(username,scope,client_id,client_secret,redirect_uri)

# all = []
# for i in subset_pl:
#     pl = ret_jordans_pl.get_playlists(i)
#     all.append(pl)

# all_pl = pd.concat(all).reset_index(drop = True)


# TODAYS_DATE = datetime.date.today().strftime("%Y-%m-%d")
# desktop = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")
# excel_name = "\\spotify_playlists " + TODAYS_DATE + "." + "xlsx"
# writer = pd.ExcelWriter(desktop + str(excel_name), engine="xlsxwriter")
# all_pl.to_excel(writer, sheet_name="total_playlist", index=False)

# for idx, item in enumerate(subset_pl):
#     df = all[idx]
#     df.to_excel(writer,sheet_name = str(item),index = False)

# writer.save()
