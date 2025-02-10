<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Multiple Image Processing</title>
</head>
<body>
    <h1>Upload Images One by One for Processing</h1>
    <form id="uploadForm" action="/upload/" method="post" enctype="multipart/form-data">
        <label for="files">Choose images (upload one at a time):</label>
        <input type="file" id="files" name="files" multiple>
        <br><br>
        <button type="submit">Upload and Process</button>
    </form>
</body>
</html>
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
import os
from app3 import process_image_pipeline  # Import your existing function

app = FastAPI()

# Ensure the "static" directory exists
if not os.path.exists("static"):
    os.makedirs("static")

# Mount the "static" directory to serve uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("many.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.post("/upload/", response_class=HTMLResponse)
async def upload_images(files: list[UploadFile] = File(...)):
    html_content = """
    <h1>Processing Results</h1>
    <div style="border: 1px solid #ccc; padding: 10px; max-height: 400px; overflow-y: scroll;">
    """
    
    for file in files:
        try:
            # Save the uploaded file
            image_path = f"static/{file.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Process the image and get the result
            result = process_image_pipeline(image_path)

            # Generate HTML content for each result
            html_content += f"""
            <h3>Image: {file.filename}</h3>
            <img src="/static/{file.filename}" alt="{file.filename}" style="max-width: 50%; height: auto;">
            <table border="1" style="border-collapse: collapse; width: 50%;">
            <tr>
                <th style="padding: 8px; background-color: #f2f2f2;">Label</th>
                <th style="padding: 8px; background-color: #f2f2f2;">Extracted Text</th>
            </tr>
            """

            for row in result:
                html_content += f"""
                <tr>
                    <td style="padding: 8px;">{row[0]}</td>
                    <td style="padding: 8px;">{row[1]}</td>
                </tr>
                """

            html_content += "</table><hr>"

        except Exception as e:
            html_content += f"<h3>Error processing {file.filename}: {str(e)}</h3><hr>"

    html_content += "</div><br><a href='/'>Upload More Images</a>"
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
