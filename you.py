
import sys
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
         { 'id': item['snippet']['resourceId']['videoId'] , 
           'title': item['snippet']['title'] , 
           'publish':item['snippet']['publishedAt']  } 

    while request:
        response = request.execute()

        items = response.get('items', [])
        assert len(items) <= 50

        videos.extend(map(video_id, filter(is_video, items)))

        request = youtube.playlistItems().list_next(
            request, response)

    return videos


if __name__ == '__main__':
    # Create YouTube Object
    youtube_object = build('youtube', 'v3', developerKey=DEV_YOUTUBE_API_KEY)
    test_channel = "UC3rqtfL5_T6dohB03peYKXg"
    test_channel = 'UCvqbFHwN-nwalWPjPUKpvTA'

    upload_playlist = get_channel_uploads_playlist_id( youtube_object ,
        test_channel)
    all_videos = get_playlist_video_ids( youtube_object , upload_playlist)
    print(all_videos)