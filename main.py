import os
import json
import base64
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QLabel, QMessageBox
from salsa20 import Salsa20

json_path = 'password_and_nonce.json'


def derive_key(password, length=32):
    """Derive a key from the password using SHA-256."""
    return hashlib.sha256(password.encode()).digest()[:length]


def generate_nonce():
    """Generate a random nonce (8 bytes)."""
    return os.urandom(8)


def encrypt_file(file_path, password):
    """Encrypt the file with Salsa20 using the provided password."""
    key = derive_key(password)
    nonce = generate_nonce()

    # Path to the JSON file

    def check_nonce(inp_nonce):
        # Check if the file exists
        enc_nonce = base64.b64encode(inp_nonce).decode('utf-8')
        if os.path.isfile(json_path):
            with open(json_path, 'r') as file:
                # json.dump(data, file, indent=4)  # indent=4 for pretty-printing
                dt = json.load(file)

            if enc_nonce not in dt.values():
                dt[password] = enc_nonce
                with open(json_path, 'w') as file:
                    json.dump(dt, file, indent=4)
                return inp_nonce
            else:
                new_nonce = generate_nonce()
                check_nonce(new_nonce)
        else:
            dt = {password: enc_nonce}
            with open(json_path, 'w') as file:
                json.dump(dt, file, indent=4)
            return inp_nonce

    nonce = check_nonce(nonce)

    # Initialize Salsa20 cipher
    salsa20 = Salsa20(key, nonce)

    encrypted_file_path = file_path + ".enc"
    with open(file_path, 'rb') as f_in, open(encrypted_file_path, 'wb') as f_out:
        # Write the nonce at the start of the file
        # f_out.write(nonce)
        encrypted_chunk = salsa20.encrypt(f_in.read())
        f_out.write(encrypted_chunk)

    return encrypted_file_path


def decrypt_file(file_path, password):
    """Decrypt the file with Salsa20 using the provided password."""
    key = derive_key(password)

    with open(file_path, 'rb') as f_in:
        # Read the nonce from the start of the file
        # nonce = f_in.read(8)
        with open(json_path, 'r') as file:
            dt = json.load(file)

        enc_nonce = dt[password]
        nonce = base64.b64decode(enc_nonce)

        salsa20 = Salsa20(key, nonce)

        decrypted_file_path = file_path.replace(".enc", ".dec")
        with open(decrypted_file_path, 'w') as f_out:
            decrypted_chunk = salsa20.decrypt(f_in.read())
            f_out.write(decrypted_chunk)

    return decrypted_file_path


class FileEncryptor(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Encryption Tool")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Labels and Text Input for Password
        self.label = QLabel("Enter password for encryption/decryption:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)

        # Buttons
        self.select_file_button = QPushButton('Select File', self)
        self.select_file_button.clicked.connect(self.select_file)

        self.encrypt_button = QPushButton('Encrypt', self)
        self.encrypt_button.clicked.connect(self.encrypt_file)

        self.decrypt_button = QPushButton('Decrypt', self)
        self.decrypt_button.clicked.connect(self.decrypt_file)

        layout.addWidget(self.select_file_button)
        layout.addWidget(self.encrypt_button)
        layout.addWidget(self.decrypt_button)

        self.setLayout(layout)

        self.file_path = None

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
        if file_path:
            self.file_path = file_path
            QMessageBox.information(self, "File Selected", f"Selected file: {self.file_path}")

    def encrypt_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "No file selected")
            return
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return

        try:
            encrypted_file = encrypt_file(self.file_path, password)
            QMessageBox.information(self, "Success", f"File encrypted successfully: {encrypted_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to encrypt file: {str(e)}")

    def decrypt_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "No file selected")
            return
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return

        try:
            decrypted_file = decrypt_file(self.file_path, password)
            QMessageBox.information(self, "Success", f"File decrypted successfully: {decrypted_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decrypt file: {str(e)}")


if __name__ == "__main__":
    app = QApplication([])

    window = FileEncryptor()
    window.show()

    app.exec_()
