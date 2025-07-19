import os
import yt_dlp
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import TEMP_DIR, MAX_FILE_SIZE, DOWNLOAD_TIMEOUT, VIDEO_QUALITY, logger
from utils import sanitize_filename, format_file_size

class VideoDownloader:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def _get_ydl_opts(self, output_path, download_thumbnail=True):
        """Get yt-dlp options."""
        return {
            'outtmpl': output_path,
            'format': VIDEO_QUALITY,
            'noplaylist': True,
            'extract_flat': False,
            'writethumbnail': download_thumbnail,
            'writeinfojson': False,
            'quiet': True,
            'no_warnings': True,
            'restrictfilenames': True,
            'ignoreerrors': False,
        }
    
    def _download_sync(self, url, output_path):
        """Synchronous download function."""
        ydl_opts = self._get_ydl_opts(output_path, download_thumbnail=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            
            if not info:
                raise Exception("Could not extract video information")
            
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # Check if video is too long (> 30 minutes)
            if duration and duration > 1800:
                raise Exception(f"Video is too long ({duration//60} minutes). Maximum allowed: 30 minutes")
            
            # Download the video with thumbnail
            ydl.download([url])
            
            # Find thumbnail file
            thumbnail_path = None
            base_name = os.path.splitext(output_path.replace('%(title)s.%(ext)s', sanitize_filename(title)))[0]
            
            # Common thumbnail extensions
            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                thumb_file = base_name + ext
                if os.path.exists(thumb_file):
                    thumbnail_path = thumb_file
                    break
            
            return {
                'title': title,
                'duration': duration,
                'filename': info.get('_filename', ''),
                'thumbnail': thumbnail_path
            }
    
    async def download_video(self, url, user_id):
        """Download video asynchronously."""
        try:
            # Create user-specific directory
            user_dir = os.path.join(TEMP_DIR, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Set output template
            output_template = os.path.join(user_dir, '%(title)s.%(ext)s')
            
            logger.info(f"Starting download for user {user_id}: {url}")
            
            # Run download in thread pool
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, self._download_sync, url, output_template),
                timeout=DOWNLOAD_TIMEOUT
            )
            
            # Find the downloaded file
            downloaded_files = []
            for file in os.listdir(user_dir):
                file_path = os.path.join(user_dir, file)
                if os.path.isfile(file_path):
                    downloaded_files.append(file_path)
            
            if not downloaded_files:
                raise Exception("No file was downloaded")
            
            # Get the most recent file (in case of multiple files)
            video_file = max(downloaded_files, key=os.path.getctime)
            
            # Check file size
            file_size = os.path.getsize(video_file)
            if file_size > MAX_FILE_SIZE:
                raise Exception(f"Video file too large ({format_file_size(file_size)}). Maximum allowed: {format_file_size(MAX_FILE_SIZE)}")
            
            logger.info(f"Download completed for user {user_id}: {video_file} ({format_file_size(file_size)})")
            
            return {
                'file_path': video_file,
                'title': result['title'],
                'size': file_size,
                'duration': result.get('duration', 0)
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Download timeout for user {user_id}: {url}")
            raise Exception("Download timed out. The video might be too large or the connection is slow.")
        except yt_dlp.DownloadError as e:
            logger.error(f"yt-dlp error for user {user_id}: {e}")
            raise Exception(f"Download failed: {str(e)}")
        except Exception as e:
            logger.error(f"Download error for user {user_id}: {e}")
            raise e
    
    async def get_video_info(self, url):
        """Get video information without downloading."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            loop = asyncio.get_event_loop()
            
            def extract_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(self.executor, extract_info)
            
            if not info:
                return None
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None

# Global instance
downloader = VideoDownloader()
