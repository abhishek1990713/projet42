<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Multiple Image Processing</title>
</head>
<body>
    <h1>Upload Multiple Images for Processing</h1>
    <form action="/upload/" method="post" enctype="multipart/form-data">
        <label for="files">Choose images:</label>
        <input type="file" id="files" name="files" multiple required>
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
    try:
        html_content = """
        <h1>Processing Results</h1>
        <h3>Uploaded Images and Extracted Information:</h3>
        """

        for file in files:
            # Save each uploaded file to the "static" directory
            image_path = f"static/{file.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Process each image and get the result
            result = process_image_pipeline(image_path)

            # Append result for each image
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

            html_content += "</table><br><br>"

        html_content += "<br><a href='/'>Upload More Images</a>"
        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1><br><a href='/'>Try Again</a>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
