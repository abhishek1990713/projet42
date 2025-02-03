
import os
import asyncio
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from concurrent.futures import ThreadPoolExecutor

# Initialize FastAPI app
app = FastAPI()

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


# Serve index.html when user visits the root URL
@app.get("/", response_class=HTMLResponse)
async def serve_html():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except Exception as e:
        logger.error(f"Error serving HTML file: {str(e)}")
        return HTMLResponse(content="<h1>Error loading page</h1>", status_code=500)


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


# Run processing in a background thread
async def process_file_async(file_path):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, process_input_file, file_path)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
