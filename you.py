

#from os import stat

import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

from googleapiclient.discovery import build

DEV_YOUTUBE_API_KEY = 'AIzaSyBwBmz-TBnfSB_NzawnlO9sgjSCN7Ik3Is'

def get_channel_uploads_playlist_id(youtube, channel_id):
    response = youtube.channels().list(
        fields = 'items/contentDetails/relatedPlaylists/uploads',
        part = 'contentDetails',
        id = channel_id,
        maxResults = 1
    ).execute()

    items = response.get('items')
    if items:
        return items[0] \
            ['contentDetails'] \
            ['relatedPlaylists'] \
            .get('uploads')
    else:
        return None

def get_playlist_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        #fields = 'nextPageToken,items/snippet/resourceId,items/snippet/title',
        fields = 'nextPageToken,items/snippet',
        playlistId = playlist_id,
        part = 'snippet',
        maxResults = 50
    )
    videos = []

    is_video = lambda item: \
        item['snippet']['resourceId']['kind'] == 'youtube#video'
    video_id = lambda item: \
         { 'id'          : item['snippet']['resourceId']['videoId'] ,
           'title'       : item['snippet']['title'],
           'publishedAt' : item['snippet']['publishedAt']
         }
    while request:
        response = request.execute()

        items = response.get('items', [])
        assert len(items) <= 50

        videos.extend(map(video_id, filter(is_video, items)))

        request = youtube.playlistItems().list_next(
            request, response)

    return videos

def get_videos_stats( youtube,  video_ids):
    stats = []
    for i in range(0, len(video_ids), 40):
        ids = [i['id'] for i in video_ids[i:i+40]]
        res = youtube.videos().list(id=','.join(ids),part='statistics').execute()
        stats += res['items']

    video_description = lambda item: \
         { 'id'          : video_ids[item]['id'] ,
           'title'       : video_ids[item]['title'],
           'publishedAt' : video_ids[item]['publishedAt'],
           'statistics'        : stats[item]['statistics']
         }        
    
    return [video_description(i) for i in range(0,len(video_ids))] 


if __name__ == '__main__':
    
    youtube_object = build('youtube', 'v3', developerKey=DEV_YOUTUBE_API_KEY)
    test_channel = "UC3rqtfL5_T6dohB03peYKXg"
    test_channel = 'UCvqbFHwN-nwalWPjPUKpvTA'

    upload_playlist = get_channel_uploads_playlist_id( youtube_object ,
        test_channel)
    all_videos = get_playlist_video_ids( youtube_object , upload_playlist)
    print(json.dumps(get_videos_stats( youtube_object, all_videos) ))