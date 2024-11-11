from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello, client! Connection is secure."})

if __name__ == '__main__':
    # SSL context configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED  # Require client certificate verification
    context.load_cert_chain(certfile='certificate.cer', keyfile='private.key')
    context.load_verify_locations(cafile='CA.pem')  # Load the CA certificate for client verification
    
    # Run the Flask app with SSL enabled
    app.run(host='127.0.0.1', port=8013, ssl_context=context)


import requests
import ssl
import socket

# Paths to the client certificate, private key, and CA certificate
CERTFILE = 'certificate.cer'   # Client certificate
KEYFILE = 'private.key'        # Client private key
KEY_PASSWORD = 'your_password_here'  # Password for the private key
CA_CERT = 'CA.pem'             # CA certificate to verify the server

# Flask server URL
url = 'https://127.0.0.1:8013/api/data'

# Using requests with client cert and CA cert to establish secure connection
try:
    response = requests.get(
        url,
        cert=(CERTFILE, KEYFILE),  # Client certificate and private key
        verify=CA_CERT             # Server CA certificate
    )
    print("Response from server:", response.json())
except requests.exceptions.SSLError as e:
    print("SSL error:", e)
except Exception as e:
    print("Error:", e)

# Direct SSL socket connection as an alternative
try:
    # Create SSL context for client-side verification
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE, password=KEY_PASSWORD)  # Load client cert and key
    context.load_verify_locations(cafile=CA_CERT)  # Load CA cert to verify server
    context.check_hostname = False  # Disable hostname check for testing; enable in production

    # Connect to the server using SSL context
    with socket.create_connection(('127.0.0.1', 8013)) as sock:
        with context.wrap_socket(sock, server_hostname='127.0.0.1') as ssock:
            print("Connected to server securely (using specified CA cert).")
            ssock.sendall(b"Hello, server")
            data = ssock.recv(1024)
            print("Received:", data.decode())
except Exception as e:
    print("Socket error:", e)
