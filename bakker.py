
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
import shutil
from app_japan import process_image_pipeline  # Import your existing function

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content


@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save uploaded file to a temporary location
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image using process_image_pipeline from app_japan.py
        result = process_image_pipeline(temp_file_path)
        
        # Generate an HTML table for the result
        html_content = """
        <h1>Processing Result</h1>
        <table border="1" style="border-collapse: collapse; width: 100%;">
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
        html_content += "</table>"
        html_content += """<br><a href="/">Upload Another Image</a>"""
        
        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1><br><a href='/'>Try Again</a>")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
