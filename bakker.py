
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
import os
from typing import List
import asyncio
from Japan_commercial_card_app import process_image_pipeline
from all_passport_app import all_passport

app = FastAPI()

# Ensure the "static" directory exists
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index_2.html", "r", encoding="utf-8") as f:
        return f.read()

async def delete_files_after_response(file_paths: List[str]):
    await asyncio.sleep(20)
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

async def process_upload(files: List[UploadFile], process_function, background_task: BackgroundTasks):
    html_content = """
    <h1>Processing Results</h1>
    <div style="border: 1px solid #ccc; padding: 10px; max-height: 600px; overflow-y: scroll;">
    """
    uploaded_file_paths = []

    for file in files:
        try:
            image_path = f"static/{file.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_file_paths.append(image_path)
            
            result = process_function(image_path)
            html_content += f"""
            <h3>Image: {file.filename}</h3>
            <img src="/static/{file.filename}" alt="{file.filename}" style="max-width: 50%; height: auto;">
            <table border="1" style="border-collapse: collapse; width: 60%;">
                <tr><th>Label</th><th>Extracted Text</th></tr>
            """
            for row in result:
                html_content += f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>"
            html_content += "</table><hr>"

        except Exception as e:
            html_content += f"<h3>Error processing {file.filename}: {str(e)}</h3><hr>"

    html_content += "</div><br><a href='/'>Upload More Images</a>"
    background_task.add_task(delete_files_after_response, uploaded_file_paths)
    return HTMLResponse(content=html_content)

@app.post("/upload_pipeline/", response_class=HTMLResponse)
async def upload_pipeline(files: List[UploadFile] = File(...), background_task: BackgroundTasks = BackgroundTasks()):
    return await process_upload(files, process_image_pipeline, background_task)

@app.post("/upload_passport/", response_class=HTMLResponse)
async def upload_passport(files: List[UploadFile] = File(...), background_task: BackgroundTasks = BackgroundTasks()):
    return await process_upload(files, all_passport, background_task)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Japan Commercial Card</title>
    <style>
        body {
            background-color: aliceblue;
            font-family: Arial, sans-serif;
        }
        #logo {
            position: absolute;
            top: 10px;
            right: 18px;
            width: 150px;
            height: auto;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        form {
            text-align: center;
            margin: 20px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            margin: 10px;
        }
        button:hover {
            background-color: #45a049;
        }
        #results {
            border: 1px solid #ccc;
            padding: 10px;
            max-height: 400px;
            overflow-y: scroll;
            margin: 20px;
        }
    </style>
</head>
<body>
    <img src="citilogo2.png" alt="Website Logo" id="logo">
    <h1>Japan Commercial Card</h1>
    <form id="uploadFormPipeline" action="/upload_pipeline/" method="post" enctype="multipart/form-data">
        <h3>Process with `process_image_pipeline`</h3>
        <label for="filesPipeline">Select Images:</label><br><br>
        <input type="file" id="filesPipeline" name="files" multiple><br><br>
        <button type="submit">Upload and Process (Pipeline)</button>
    </form>
    <form id="uploadFormPassport" action="/upload_passport/" method="post" enctype="multipart/form-data">
        <h3>Process with `all_passport`</h3>
        <label for="filesPassport">Select Images:</label><br><br>
        <input type="file" id="filesPassport" name="files" multiple><br><br>
        <button type="submit">Upload and Process (Passport)</button>
    </form>
    <h2>Uploaded Files and Results:</h2>
    <div id="results">
        <!-- Processed results will appear here -->
    </div>
    <script>
        const pipelineForm = document.getElementById('uploadFormPipeline');
        const passportForm = document.getElementById('uploadFormPassport');
        const resultsDiv = document.getElementById('results');

        pipelineForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await uploadFiles(event.target, '/upload_pipeline/');
        });

        passportForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await uploadFiles(event.target, '/upload_passport/');
        });

        async function uploadFiles(form, endpoint) {
            const formData = new FormData(form);
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.text();
                resultsDiv.innerHTML += result + '<hr>';
                form.reset();
            } catch (error) {
                resultsDiv.innerHTML += `<p style="color: red;">Error: ${error.message}</p><hr>`;
            }
        }
    </script>
</body>
</html>
