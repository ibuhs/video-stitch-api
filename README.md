# Video Stitch API

A FastAPI-based REST API that stitches multiple MP4 video files together into a single video.

## Features

- Accepts 2-5 MP4 video files
- Stitches videos using FFmpeg's concat method
- Returns the final stitched video as a downloadable file
- Includes health check endpoint
- CORS enabled
- Automatic cleanup of temporary files

## Prerequisites

- Python 3.10+
- FFmpeg installed on the system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/video-stitch-api.git
cd video-stitch-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install FFmpeg (if not already installed):
- On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```
- On macOS:
```bash
brew install ffmpeg
```

## Running the API

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

The API will be available at `http://localhost:10000`

## API Endpoints

### POST /stitch
Stitches multiple video files together.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: 2-5 MP4 video files

**Response:**
- Content-Type: video/mp4
- Body: Stitched video file

### GET /health
Health check endpoint for monitoring.

**Response:**
```json
{
    "status": "healthy"
}
```

## Testing with curl

```bash
curl -X POST -F "files=@video1.mp4" -F "files=@video2.mp4" http://localhost:10000/stitch --output stitched_video.mp4
```

## Deployment

### Render.com

1. Create a new Web Service
2. Connect your GitHub repository
3. Use Python 3.10+
4. Set the start command:
```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```
5. Add build command to install FFmpeg:
```bash
apt-get update && apt-get install -y ffmpeg
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 400: Invalid input (wrong number of files or non-MP4 files)
- 500: FFmpeg processing errors

## License

MIT 