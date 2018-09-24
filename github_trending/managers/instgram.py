import os
import logging
from tempfile import TemporaryDirectory

from InstagramAPI import InstagramAPI
import ffmpy
import requests
from PIL import Image
import moviepy.editor as mp


_logger = logging.getLogger(__name__)


def post_trending_repo(repo):
    temp_dir = TemporaryDirectory()

    if not _should_post_repo(repo):
        _logger.info(f"Not appropriate for posting: {repo.link}")
        return

    gif = _download_gif_file(repo.gif_link, directory=temp_dir)
    mp4 = _convert_gif_to_mp4(gif, output_directory=temp_dir)
    shortened_mp4 = _shorten_video(mp4, directory=temp_dir)
    resized_mp4 = _resize_video(shortened_mp4, directory=temp_dir)
    thumbnail = _generate_thumbnail_from_video(resized_mp4, directory=temp_dir)
    caption = _generate_caption(repo=repo)

    instagram_client = InstagramAPI(
        "github_trending_videos", os.environ.get('INSTAGRAM_PASSWORD'))
    instagram_client.login()  # login

    instagram_client.uploadVideo(
        resized_mp4, thumbnail, caption=caption)

    temp_dir.cleanup()


def _generate_caption(*, repo):
    return (
        f"\n{repo.title}\n\n{repo.link}\n{repo.description}\n"
        f"{repo.introduction}"
    )


def _should_post_repo(repo):
    return repo.gif_link and not repo.posted


def _convert_gif_to_mp4(gif_file, *, output_directory):
    _logger.info(f"Converting {gif_file} to mp4")
    mp4_path = output_directory.name + '/vid.mp4'
    ff = ffmpy.FFmpeg(
        inputs={gif_file: None},
        outputs={mp4_path: '-vf scale=800:800:force_original_aspect_ratio=decrease,pad=800:800:(ow-iw)/2:(oh-ih)/2,setsar=1'}
    )
    ff.run()
    return mp4_path


def _download_gif_file(gif_link, *, directory):
    _logger.info(f"Downloading {gif_link}")
    resp = requests.get(gif_link, allow_redirects=True)
    path = f"{directory.name}/gif.gif"
    with open(path, 'w+b') as f:
        f.write(resp.content)
    return path


def _resize_video(video, *, directory):
    clip = mp.VideoFileClip(video)
    clip_resized = clip.resize(width=800)
    output_file = directory.name + '/resized_video.mp4'
    clip_resized.write_videofile(output_file)
    return output_file


def _shorten_video(video, *, directory):
    clip = mp.VideoFileClip(video)
    if clip.duration < 59:
        return video
    shortened_vid = clip.subclip((0, 0), (0, 59))
    output_file = directory.name + '/shortened_video.mp4'
    shortened_vid.write_videofile(output_file)
    return output_file


def _generate_thumbnail_from_video(video_path, *, directory):
    _logger.info(f"Generating thumbnail from {video_path}")
    output_path_png = directory.name + '/thumbnail.png'
    output_path_jpeg = directory.name + '/thumbnail.jpeg'
    ff = ffmpy.FFmpeg(
        inputs={video_path: None},
        outputs={output_path_png: ['-ss', '00:00:1', '-vframes', '1']})
    ff.run()
    old_im = Image.open(output_path_png)
    old_size = old_im.size

    new_size = (800, 800)
    new_im = Image.new("RGB", new_size, color=(0, 0, 0))
    new_im.paste(old_im, (
        int((new_size[0]-old_size[0])/2),
        int((new_size[1]-old_size[1])/2)
        )
    )

    with open(output_path_jpeg, 'w+b') as f:
        new_im.save(f, format='JPEG')
    return output_path_jpeg
