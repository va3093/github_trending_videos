from InstagramAPI import InstagramAPI

InstagramAPI = InstagramAPI("github_trending_videos", "golFu98aji")
InstagramAPI.login()  # login

photo_path = '3.jpg'
video_path = '5.mp4'
caption = "Test"
InstagramAPI.uploadVideo(video_path, photo_path, caption=caption)