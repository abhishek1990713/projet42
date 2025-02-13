
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
            justify-content: space-between;
            margin: 20px;
        }
        .form-section {
            width: 48%;
            border: 1px solid #ccc;
            padding: 20px;
            background-color: white;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        form {
            text-align: center;
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
            margin: 20px;
            border: 1px solid #ccc;
            padding: 10px;
            max-height: 400px;
            overflow-y: scroll;
        }
    </style>
</head>
<body>
    <img src="citilogo2.png" alt="Website Logo" id="logo">
    <h1>Japan Commercial Card</h1>
    <div class="container">
        <div class="form-section">
            <h2>Process with <code>process_image_pipeline</code></h2>
            <form id="uploadFormPipeline" action="/upload_pipeline/" method="post" enctype="multipart/form-data">
                <label for="filesPipeline">Select Images:</label><br><br>
                <input type="file" id="filesPipeline" name="files" multiple><br><br>
                <button type="submit">Upload and Process (Pipeline)</button>
            </form>
        </div>
        <div class="form-section">
            <h2>Process with <code>all_passport</code></h2>
            <form id="uploadFormPassport" action="/upload_passport/" method="post" enctype="multipart/form-data">
                <label for="filesPassport">Select Images:</label><br><br>
                <input type="file" id="filesPassport" name="files" multiple><br><br>
                <button type="submit">Upload and Process (Passport)</button>
            </form>
        </div>
    </div>
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
