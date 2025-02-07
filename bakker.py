
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FastAPI Image Processing</title>
</head>
<body>
    <h1>Upload an Image for Processing</h1>
    <form action="/upload/" method="post" enctype="multipart/form-data">
        <label for="file">Choose an image:</label>
        <input type="file" id="file" name="file" required>
        <br><br>
        <button type="submit">Upload and Process</button>
    </form>
</body>
</html>

