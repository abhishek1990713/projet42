
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
        .container {
            display: flex;
            margin: 20px;
        }
        .image-section, .result-section {
            width: 48%;
            border: 1px solid #ccc;
            padding: 20px;
            background-color: white;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .image-section img {
            max-width: 100%;
            height: auto;
            display: block;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <img src="citilogo2.png" alt="Website Logo" id="logo">
    <h1>Japan Commercial Card</h1>
    <form id="uploadForm" action="/upload/" method="post" enctype="multipart/form-data">
        <label for="files">Select an Image:</label><br><br>
        <input type="file" id="files" name="files"><br><br>
        <button type="submit">Upload and Process</button>
    </form>

    <div class="container">
        <div class="image-section" id="imageSection">
            <h2>Uploaded Image</h2>
            <p>No image uploaded yet.</p>
        </div>
        <div class="result-section" id="resultSection">
            <h2>Processed Results</h2>
            <table id="resultTable">
                <thead>
                    <tr>
                        <th>Label</th>
                        <th>Extracted Text</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td colspan="2">No results yet.</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const imageSection = document.getElementById('imageSection');
        const resultTable = document.getElementById('resultTable').querySelector('tbody');

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(form);

            try {
                const response = await fetch('/upload/', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json(); // Assuming the server returns a JSON object with image URL and extracted data

                displayImage(result.image_url);
                displayResults(result.data);
            } catch (error) {
                imageSection.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        });

        function displayImage(imageUrl) {
            imageSection.innerHTML = `
                <h2>Uploaded Image</h2>
                <img src="${imageUrl}" alt="Uploaded Image">
            `;
        }

        function displayResults(data) {
            resultTable.innerHTML = ''; // Clear previous results
            data.forEach(row => {
                resultTable.innerHTML += `
                    <tr>
                        <td>${row.label}</td>
                        <td>${row.text}</td>
                    </tr>
                `;
            });
        }
    </script>
</body>
</html>

