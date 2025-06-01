# Video Stitch API

A FastAPI-based REST API that stitches multiple MP4 video files into a single video using FFmpeg.

## Features

- Accepts 2-5 MP4 video files
- Stitches videos using FFmpeg's concat demuxer
- Returns a single MP4 file
- Automatic cleanup of temporary files
- Health check endpoint for monitoring

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y ffmpeg
```

3. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

## API Usage

### Stitch Videos
```bash
curl -X POST -F "files=@video1.mp4" -F "files=@video2.mp4" http://localhost:10000/stitch --output stitched_video.mp4
```

### Health Check
```bash
curl http://localhost:10000/health
```

## Deployment

### Render.com

1. Fork this repository
2. Create a new Web Service on Render.com
3. Connect your GitHub repository
4. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`

The service will be automatically deployed and available at `https://your-app-name.onrender.com`

## API Endpoints

- `POST /stitch`: Stitch multiple video files
  - Accepts 2-5 MP4 files
  - Returns a single MP4 file
- `GET /health`: Health check endpoint
  - Returns `{"status": "healthy"}`

## Error Handling

- Returns 400 for invalid input (wrong number of files or non-MP4 files)
- Returns 500 for FFmpeg processing errors
- Includes detailed error messages in the response

## License

MIT 