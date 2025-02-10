
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
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        image_path = f"static/{file.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the image and get the result
        result = process_image_pipeline(image_path)

        # Generate HTML content for this result
        html_content = f"""
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

        html_content += "</table><br>"
        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)



<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Multiple Sequential Image Upload</title>
</head>
<body>
    <h1>Upload Images One by One for Processing</h1>
    <form id="uploadForm" action="/upload/" method="post" enctype="multipart/form-data">
        <label for="file">Choose an image:</label>
        <input type="file" id="file" name="file" required>
        <br><br>
        <button type="submit">Upload and Process</button>
    </form>

    <h2>Uploaded Files and Results:</h2>
    <div id="results" style="border: 1px solid #ccc; padding: 10px; max-height: 400px; overflow-y: scroll;">
        <!-- Processed results will appear here -->
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const resultsDiv = document.getElementById('results');

        form.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent form submission
            const formData = new FormData(form);
            
            // Send the file to the server using fetch
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });

            const result = await response.text();
            // Append the result to the resultsDiv
            resultsDiv.innerHTML += result + '<hr>';
            form.reset(); // Reset the form for the next file
        });
    </script>
</body>
</html>

