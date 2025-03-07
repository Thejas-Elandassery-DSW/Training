import yt_dlp
import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, session
import threading
import time
import uuid
import json
from datetime import datetime, timedelta
from youtube_browser_helper import get_youtube_cookies

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'thejas-12345-thejas')

# Dictionary to store download jobs
download_jobs = {}
# Dictionary to track user sessions and their files
user_sessions = {}
# Cleanup interval in seconds
CLEANUP_INTERVAL = 3600  # 1 hour
# Session expiry time in seconds
SESSION_EXPIRY = 1800  # 30 minutes

class DownloadJob:
    def __init__(self, url, directory, format_type, session_id):
        self.id = str(uuid.uuid4())
        self.url = url
        self.directory = directory
        self.format_type = format_type
        self.session_id = session_id
        self.status = "pending"
        self.progress = 0
        self.current_file = ""
        self.speed = "N/A"
        self.eta = "N/A"
        self.error = None
        self.temp_files = []  # Track all files (temporary and final)
        self.completed_files = []  # Only final output files after conversion
        self.started_at = datetime.now()
        self.completed_at = None
        
    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "directory": self.directory,
            "format_type": self.format_type,
            "status": self.status,
            "progress": self.progress,
            "current_file": self.current_file,
            "speed": self.speed,
            "eta": self.eta,
            "error": self.error,
            "completed_files": self.completed_files,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

def update_status(job, d):
    if d['status'] == 'downloading':
        try:
            # Update progress
            job.progress = float(d.get('_percent_str', '0').replace('%', ''))
            
            # Update status with filename and progress
            filename = d.get('filename', '').split('/')[-1]
            job.current_file = filename
            job.speed = d.get('_speed_str', 'N/A')
            job.eta = d.get('_eta_str', 'N/A')
            job.status = "downloading"
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            
    elif d['status'] == 'finished':
        filename = d.get('filename', '').split('/')[-1]
        job.current_file = filename
        job.temp_files.append(filename)
        job.status = "processing"
        
    elif d['status'] == 'error':
        job.error = d.get('error', 'Unknown error')
        job.status = "error"

def download_playlist(job_id):
    job = download_jobs[job_id]
    
    try:
        url = job.url
        download_path = job.directory
        format_type = job.format_type
        
        # Add debugging
        print(f"Download path: {download_path}")
        print(f"URL: {url}")
        print(f"Format: {format_type}")
        
        # Make sure the directory exists
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            print(f"Created directory: {download_path}")
        else:
            print(f"Directory already exists: {download_path}")
        
        def progress_hook(d):
            update_status(job, d)
        
        # Get YouTube cookies to bypass bot detection
        job.status = "getting cookies"
        job.current_file = "Preparing browser to bypass YouTube restrictions..."
        cookie_file = get_youtube_cookies(url)
        
        # Common options to help bypass YouTube's bot detection
        common_opts = {
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'quiet': False,
            'verbose': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'extractor_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.youtube.com/',
            }
        }
        
        # Add cookies if available
        if cookie_file:
            common_opts['cookiefile'] = cookie_file
        
        # Format-specific options
        if format_type == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'keepvideo': False,  # Don't keep the video file after conversion
            }
        elif format_type == 'mp4':
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            }
        elif format_type == 'webm':
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'webm',
            }
        
        # Merge common options with format-specific options
        ydl_opts.update(common_opts)
        
        job.status = "starting"
        print(f"Starting download with format: {format_type}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get actual output files after download is complete
            if 'entries' in info:
                # It's a playlist
                entries = list(info['entries'])
                for entry in entries:
                    if 'requested_downloads' in entry:
                        for download in entry['requested_downloads']:
                            final_filename = os.path.basename(download.get('filepath', ''))
                            if final_filename and final_filename not in job.completed_files:
                                job.completed_files.append(final_filename)
            else:
                # It's a single video
                if 'requested_downloads' in info:
                    for download in info['requested_downloads']:
                        final_filename = os.path.basename(download.get('filepath', ''))
                        if final_filename and final_filename not in job.completed_files:
                            job.completed_files.append(final_filename)
        
        # If no completed files were detected, check the directory for files with the correct extension
        if not job.completed_files:
            expected_ext = '.mp3' if format_type == 'mp3' else ('.mp4' if format_type == 'mp4' else '.webm')
            for file in os.listdir(download_path):
                if file.endswith(expected_ext) and file not in job.completed_files:
                    # Check if file was created after job started
                    file_path = os.path.join(download_path, file)
                    if os.path.getctime(file_path) >= job.started_at.timestamp():
                        job.completed_files.append(file)
        
        job.status = "completed"
        job.completed_at = datetime.now()
        job.current_file = "All downloads completed"
        
        # Update the user's session data with these new files
        if job.session_id in user_sessions:
            user_sessions[job.session_id]['files'].extend(job.completed_files)
            user_sessions[job.session_id]['last_activity'] = datetime.now()
        
    except Exception as e:
        job.status = "error"
        job.error = str(e)
        print(f"Error occurred: {str(e)}")

def cleanup_old_sessions():
    """Periodically clean up expired sessions and their files"""
    while True:
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            # Find expired sessions
            for session_id, session_data in user_sessions.items():
                last_activity = session_data.get('last_activity')
                if last_activity and (current_time - last_activity) > timedelta(seconds=SESSION_EXPIRY):
                    expired_sessions.append(session_id)
            
            # Clean up expired sessions
            for session_id in expired_sessions:
                cleanup_session(session_id)
                print(f"Cleaned up expired session: {session_id}")
            
            # Clean up jobs for expired sessions
            jobs_to_remove = []
            for job_id, job in download_jobs.items():
                if hasattr(job, 'session_id') and job.session_id in expired_sessions:
                    jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del download_jobs[job_id]
                
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            
        # Sleep before next cleanup cycle
        time.sleep(CLEANUP_INTERVAL)

def cleanup_session(session_id):
    """Clean up files for a specific session"""
    if session_id in user_sessions:
        session_dir = user_sessions[session_id].get('directory')
        files = user_sessions[session_id].get('files', [])
        
        # Delete individual files
        for filename in files:
            try:
                file_path = os.path.join(session_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {filename}: {str(e)}")
        
        # Remove the session data
        del user_sessions[session_id]

@app.route('/')
def index():
    # Create or get a session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
    session_id = session['session_id']
    
    # Create a session directory if it doesn't exist
    session_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], session_id)
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    
    # Initialize or update session data
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'directory': session_dir,
            'files': [],
            'last_activity': datetime.now()
        }
    else:
        user_sessions[session_id]['last_activity'] = datetime.now()
    
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    url = request.form.get('url')
    format_type = request.form.get('format', 'webm')  # Default to webm if not specified
    
    if not url:
        return jsonify({"error": "Please enter a valid URL"}), 400
    
    # Validate format_type
    if format_type not in ['mp3', 'mp4', 'webm']:
        return jsonify({"error": "Invalid format type. Choose mp3, mp4, or webm"}), 400
    
    # Get or create session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_id = session['session_id']
    
    # Set download directory to the session-specific directory
    download_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], session_id)
    
    # Make sure it exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Update session tracking
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'directory': download_dir,
            'files': [],
            'last_activity': datetime.now()
        }
    else:
        user_sessions[session_id]['last_activity'] = datetime.now()
    
    # Log the download request
    print(f"Download requested: URL={url}, FORMAT={format_type}, DIR={download_dir}, SESSION={session_id}")
    
    job = DownloadJob(url, download_dir, format_type, session_id)
    download_jobs[job.id] = job
    
    # Start download thread
    thread = threading.Thread(target=download_playlist, args=(job.id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"job_id": job.id})

@app.route('/status/<job_id>')
def get_status(job_id):
    # Update session activity timestamp
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in user_sessions:
            user_sessions[session_id]['last_activity'] = datetime.now()
    
    if job_id in download_jobs:
        return jsonify(download_jobs[job_id].to_dict())
    
    return jsonify({"error": "Job not found"}), 404

@app.route('/jobs')
def list_jobs():
    # Update session activity timestamp
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in user_sessions:
            user_sessions[session_id]['last_activity'] = datetime.now()
        
        # Only return jobs for this session
        session_jobs = [job.to_dict() for job_id, job in download_jobs.items() 
                        if hasattr(job, 'session_id') and job.session_id == session_id]
        return jsonify(session_jobs)
    
    return jsonify([])

@app.route('/downloads/<path:filename>')
def download_file(filename):
    # Update session activity timestamp
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in user_sessions:
            user_sessions[session_id]['last_activity'] = datetime.now()
            session_dir = user_sessions[session_id]['directory']
            
            # Check if file exists in session directory
            file_path = os.path.join(session_dir, filename)
            if os.path.exists(file_path):
                return send_from_directory(session_dir, filename, as_attachment=True)
    
    return f"File not found: {filename}", 404

@app.route('/formats')
def get_formats():
    # API endpoint to get available formats
    return jsonify({
        "formats": [
            {"id": "mp3", "name": "MP3 Audio"},
            {"id": "mp4", "name": "MP4 Video"},
            {"id": "webm", "name": "WebM Video"}
        ]
    })

@app.route('/clear-history', methods=['POST'])
def clear_history():
    # Clear download job history for this session only
    if 'session_id' in session:
        session_id = session['session_id']
        
        # Find all jobs for this session
        jobs_to_remove = []
        for job_id, job in download_jobs.items():
            if hasattr(job, 'session_id') and job.session_id == session_id:
                jobs_to_remove.append(job_id)
        
        # Remove the jobs
        for job_id in jobs_to_remove:
            del download_jobs[job_id]
        
        # Clean up session files
        cleanup_session(session_id)
        
        # Re-initialize the session data
        session_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], session_id)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
            
        user_sessions[session_id] = {
            'directory': session_dir,
            'files': [],
            'last_activity': datetime.now()
        }
        
    return jsonify({"status": "success", "message": "Download history cleared"})

@app.route('/ping', methods=['POST'])
def ping():
    """Update the session's last activity timestamp"""
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in user_sessions:
            user_sessions[session_id]['last_activity'] = datetime.now()
    return jsonify({"status": "success"})

@app.before_request
def before_request():
    """Update session timestamp on every request"""
    if 'session_id' in session:
        session_id = session['session_id']
        if session_id in user_sessions:
            user_sessions[session_id]['last_activity'] = datetime.now()

if __name__ == "__main__":
    # Define download folder from environment variable or use default
    download_folder = os.environ.get('DOWNLOAD_FOLDER', '/tmp/downloads')
    app.config['DOWNLOAD_FOLDER'] = download_folder
    
    # Create main download directory if it doesn't exist
    if not os.path.exists(download_folder):
        try:
            os.makedirs(download_folder)
            print(f"Created main download directory: {download_folder}")
        except Exception as e:
            print(f"Error creating directory {download_folder}: {str(e)}")
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_sessions)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    # Print startup information
    print(f"YouTube Downloader starting...")
    print(f"Main download folder: {app.config['DOWNLOAD_FOLDER']}")
    print(f"Session expiry time: {SESSION_EXPIRY} seconds")
    print(f"Cleanup interval: {CLEANUP_INTERVAL} seconds")
    
    # Use debug mode only in development
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
