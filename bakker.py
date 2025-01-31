
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Upload</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 50px;
        }
        #output {
            margin-top: 20px;
            font-weight: bold;
        }
        input[type="file"] {
            margin: 20px;
        }
        button {
            padding: 10px 20px;
            background-color: blue;
            color: white;
            border: none;
            cursor: pointer;
        }
        button:hover {
            background-color: darkblue;
        }
    </style>
</head>
<body>

    <h2>Upload File</h2>
    <input type="file" id="fileInput" accept="image/*,application/pdf">
    <button onclick="uploadFile()">Upload</button>
    
    <div id="output"></div>

    <script>
        async function uploadFile() {
            const fileInput = document.getElementById("fileInput");
            if (fileInput.files.length === 0) {
                alert("Please select a file!");
                return;
            }

            let formData = new FormData();
            formData.append("file", fileInput.files[0]);

            try {
                document.getElementById("output").innerText = "Processing...";
                let response = await fetch("http://127.0.0.1:8888/process-file/", {
                    method: "POST",
                    body: formData
                });

                let result = await response.json();
                if (response.ok) {
                    document.getElementById("output").innerText = "Result: " + JSON.stringify(result.result);
                } else {
                    document.getElementById("output").innerText = "Error: " + result.detail;
                }
            } catch (error) {
                document.getElementById("output").innerText = "Request failed!";
                console.error("Error:", error);
            }
        }
    </script>

</body>
</html>
