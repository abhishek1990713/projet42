
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
from app_japan import process_image_pipeline

app = FastAPI()

# Ensure the "static" directory exists
if not os.path.exists("static"):
    os.makedirs("static")

# Mount the "static" directory to serve uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(file: UploadFile = File(...)):
    try:
        image_path = f"static/{file.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_image_pipeline(image_path)

        html_content = f"""
        <h1>Processing Result</h1>
        <h3>Uploaded Image:</h3>
        <img src="/{image_path}" alt="Uploaded Image" style="max-width: 100%; height: auto;">
        <h3>Extracted Information:</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th style="padding: 8px; background-color: #f2f2f2;">Label</th>
                <th style="padding: 8px; background-color: #f2f2f2;">Extracted Text</th>
            </tr>
        """
        for row in result:
            html_content += f"""
            <tr>
                <td style="padding: 8px;">{row['Label']}</td>
                <td style="padding: 8px;">{row['Extracted_text']}</td>
            </tr>
            """
        html_content += "</table><br><a href='/'>Upload Another Image</a>"

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1><br><a href='/'>Try Again</a>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
