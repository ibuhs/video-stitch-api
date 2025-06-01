import os
import uuid
import subprocess
from typing import List
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import tempfile
import logging
import pathlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Stitch API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy"}

@app.post("/stitch")
async def stitch_videos(files: List[UploadFile], background_tasks: BackgroundTasks):
    """
    Stitch multiple video files together into a single MP4 file.
    Accepts 2-5 MP4 files and returns the stitched video.
    """
    if not 2 <= len(files) <= 5:
        raise HTTPException(status_code=400, detail="Please upload between 2 and 5 video files")
    
    # Create a temporary directory
    temp_dir = pathlib.Path(tempfile.mkdtemp())
    logger.info(f"Created temporary directory: {temp_dir}")
    
    # Generate unique filenames for uploaded files
    temp_files = []
    list_file_path = temp_dir / "list.txt"
    output_file = temp_dir / "output.mp4"
    
    try:
        # Save uploaded files
        for file in files:
            if not file.filename.lower().endswith('.mp4'):
                raise HTTPException(status_code=400, detail="Only MP4 files are allowed")
            
            temp_filename = temp_dir / f"{uuid.uuid4()}.mp4"
            logger.info(f"Saving uploaded file to: {temp_filename}")
            
            # Read the entire file content
            content = await file.read()
            logger.info(f"Read {len(content)} bytes from uploaded file")
            
            # Write the content to the temporary file
            with open(temp_filename, "wb") as buffer:
                buffer.write(content)
            
            # Verify the file was written correctly
            if not temp_filename.exists():
                raise HTTPException(status_code=500, detail=f"Failed to save file {file.filename}")
            
            file_size = temp_filename.stat().st_size
            logger.info(f"Saved file {temp_filename} with size {file_size} bytes")
            
            temp_files.append(str(temp_filename))
        
        # Create list.txt file for FFmpeg
        logger.info(f"Creating list file at: {list_file_path}")
        with open(list_file_path, "w") as f:
            for temp_file in temp_files:
                f.write(f"file '{temp_file}'\n")
        
        # Run FFmpeg command
        logger.info("Running FFmpeg command")
        try:
            cmd = [
                "ffmpeg", "-f", "concat", "-safe", "0",
                "-i", str(list_file_path), "-c", "copy", str(output_file)
            ]
            logger.info(f"FFmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"FFmpeg stdout: {result.stdout}")
            logger.info(f"FFmpeg stderr: {result.stderr}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg processing failed: {e.stderr}"
            )
        
        # Verify output file exists and has content
        if not output_file.exists():
            logger.error(f"Output file not found at: {output_file}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create output video file"
            )
        
        file_size = output_file.stat().st_size
        logger.info(f"Output file size: {file_size} bytes")
        
        if file_size < 1024:  # Less than 1KB
            logger.error(f"Output file too small: {file_size} bytes")
            raise HTTPException(
                status_code=500,
                detail="Output video file is too small, processing may have failed"
            )
        
        # Read the output file into memory
        with open(output_file, "rb") as f:
            content = f.read()
        
        logger.info(f"Read {len(content)} bytes from output file")
        
        # Create a temporary file to serve
        serve_file = temp_dir / "serve.mp4"
        with open(serve_file, "wb") as f:
            f.write(content)
        
        logger.info(f"Created serve file with size {serve_file.stat().st_size} bytes")
        
        background_tasks.add_task(shutil.rmtree, temp_dir, ignore_errors=True)
        return FileResponse(
            str(serve_file),
            media_type="video/mp4",
            filename="stitched_video.mp4"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000) 