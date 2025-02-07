
import os
import asyncio
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from apps import process_input_file  # Assuming process_input_file is your function

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(
    filename="api_processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


@app.get("/", response_class=HTMLResponse)
async def serve_html():
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    except Exception as e:
        logger.error(f"Error serving HTML file: {str(e)}")
        return HTMLResponse(content="<h1>Error loading page</h1>", status_code=500)


@app.post("/process-file/", response_class=HTMLResponse)
async def process_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"Received file: {file.filename}")

        # Process the file asynchronously
        result = await process_file_async(file_path)

        # Clean up the temporary file
        os.remove(file_path)

        # Convert the result dictionary into an HTML table
        table_html = generate_html_table(result)

        return HTMLResponse(content=table_html, status_code=200)

    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during processing.")


async def process_file_async(file_path: str):
    """
    Run the file processing in a background thread for non-blocking behavior.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, process_input_file, file_path)
    return result


def generate_html_table(data: dict) -> str:
    """
    Generate an HTML table from a dictionary.
    """
    html = """
    <table border="1" style="border-collapse: collapse; width: 80%; margin: 20px auto;">
        <tr>
            <th style="padding: 8px; background-color: #f2f2f2; text-align: left;">Label</th>
            <th style="padding: 8px; background-color: #f2f2f2; text-align: left;">Extracted Text</th>
        </tr>
    """
    for key, value in data.items():
        html += f"""
        <tr>
            <td style="padding: 8px; text-align: left;">{key}</td>
            <td style="padding: 8px; text-align: left;">{value}</td>
        </tr>
        """
    html += "</table>"
    return html


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8888)
