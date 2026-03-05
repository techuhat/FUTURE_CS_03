from flask import Flask, request, render_template, send_file
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
KEY = b'ThisIsASecretKey'  # 16 byte key for AES

# Encrypt file
def encrypt_file(data):
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext

# Decrypt file
def decrypt_file(data):
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        data = file.read()

        encrypted = encrypt_file(data)

        filepath = os.path.join(UPLOAD_FOLDER, file.filename + ".enc")
        with open(filepath, "wb") as f:
            f.write(encrypted)

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_file(encrypted_data)

    output_file = "decrypted_" + filename.replace(".enc", "")

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
