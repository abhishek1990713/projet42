
import logging
import os
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (Optional, useful if accessing from another domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (for CSS, JS, images if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(
    filename="api_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


# Dummy file processing function (Replace with actual logic)
def process_input_file(file_path):
    return f"Processed file: {file_path}"


# Serve index.html
@app.get("/", response_class=HTMLResponse)
async def serve_html():
    with open("index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read(), status_code=200)


# API Endpoint to process uploaded files
@app.post("/process-file/")
async def process_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        logger.info(f"Received file: {file.filename}")

        # Process file asynchronously
        result = await process_file_async(file_path)

        # Clean up temporary file
        os.remove(file_path)

        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during processing.")


async def process_file_async(file_path):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, process_input_file, file_path)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
