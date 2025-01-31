

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
        .container {
            width: 50%;
            margin: auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        input[type="file"] {
            margin: 20px 0;
        }
        button {
            padding: 10px 20px;
            background-color: blue;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
            border-radius: 5px;
        }
        button:hover {
            background-color: darkblue;
        }
        .output-box {
            margin-top: 20px;
            padding: 15px;
            border: 2px solid #000;
            border-radius: 5px;
            min-height: 50px;
            width: 80%;
            margin-left: auto;
            margin-right: auto;
            text-align: center;
            background-color: #f9f9f9;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="container">
        <h2>Upload File</h2>
        <input type="file" id="fileInput" accept="image/*,application/pdf">
        <button onclick="uploadFile()">Upload</button>
        <div id="output" class="output-box">Result will appear here</div>
    </div>

    <script>
        async function uploadFile() {
            const fileInput = document.getElementById("fileInput");
            const outputBox = document.getElementById("output");

            if (fileInput.files.length === 0) {
                alert("Please select a file!");
                return;
            }

            let formData = new FormData();
            formData.append("file", fileInput.files[0]);

            try {
                outputBox.innerText = "Processing...";
                let response = await fetch("http://127.0.0.1:8888/process-file/", {
                    method: "POST",
                    body: formData
                });

                let result = await response.json();
                if (response.ok) {
                    outputBox.innerText = "Result: " + JSON.stringify(result.result, null, 2);
                } else {
                    outputBox.innerText = "Error: " + result.detail;
                }
            } catch (error) {
                outputBox.innerText = "Request failed!";
                console.error("Error:", error);
            }
        }
    </script>

</body>
</html>
