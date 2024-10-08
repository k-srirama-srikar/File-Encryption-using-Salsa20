import struct
import numpy as np


class Salsa20:
    """
    Salsa20 cipher implementation.
    Supports both 128-bit and 256-bit keys.
    """
    TAU = (0x61707865, 0x3120646e, 0x79622d36, 0x6b206574)
    SIGMA = (0x61707865, 0x3320646e, 0x79622d32, 0x6b206574)
    REPEATS = 20

    def __init__(self, key: bytes, nonce: bytes):
        """
        Initialize the Salsa20 cipher with a 16-byte (128-bit) or 32-byte (256-bit) key and an 8-byte (64-bit) nonce.
        """
        if len(key) not in (16, 32):
            raise ValueError("Key must be 16 or 32 bytes long.")
        if len(nonce) != 8:
            raise ValueError("Nonce must be 8 bytes long.")

        # Set constants
        self.constants = self.TAU if len(key) == 16 else self.SIGMA

        # Split key, nonce, and prepare initial state
        k = list(struct.unpack('<4I', key[:16])) + list(struct.unpack('<4I', key[16:])) if len(key) == 32 else list(
            struct.unpack('<4I', key))
        n = list(struct.unpack('<2I', nonce))
        c = [0, 0]  # Counter set to zero

        # Initialize the 16-element state array
        self.state = np.array([
            self.constants[0], k[0], k[1], k[2], k[3],
            self.constants[1], n[0], n[1], c[0], c[1],
            self.constants[2], k[4] if len(k) > 4 else k[0], k[5] if len(k) > 4 else k[1], k[6] if len(k) > 4 else k[2],
            k[7] if len(k) > 4 else k[3],
            self.constants[3]
        ], dtype=np.uint32)

    def _rotate_left(self, a, b):
        return ((a << b) | (a >> (32 - b))) & 0xffffffff

    def _quarter_round(self, y0, y1, y2, y3):
        y1 ^= self._rotate_left((y0 + y3) & 0xffffffff, 7)
        y2 ^= self._rotate_left((y1 + y0) & 0xffffffff, 9)
        y3 ^= self._rotate_left((y2 + y1) & 0xffffffff, 13)
        y0 ^= self._rotate_left((y3 + y2) & 0xffffffff, 18)
        return y0, y1, y2, y3

    def _row_round(self, y):
        y[0], y[1], y[2], y[3] = self._quarter_round(y[0], y[1], y[2], y[3])
        y[5], y[6], y[7], y[4] = self._quarter_round(y[5], y[6], y[7], y[4])
        y[10], y[11], y[8], y[9] = self._quarter_round(y[10], y[11], y[8], y[9])
        y[15], y[12], y[13], y[14] = self._quarter_round(y[15], y[12], y[13], y[14])
        return y

    def _column_round(self, y):
        y[0], y[4], y[8], y[12] = self._quarter_round(y[0], y[4], y[8], y[12])
        y[5], y[9], y[13], y[1] = self._quarter_round(y[5], y[9], y[13], y[1])
        y[10], y[14], y[2], y[6] = self._quarter_round(y[10], y[14], y[2], y[6])
        y[15], y[3], y[7], y[11] = self._quarter_round(y[15], y[3], y[7], y[11])
        return y

    def _double_round(self, y):
        return self._row_round(self._column_round(y))

    def _salsa20_block(self):
        x = self.state.copy()
        for _ in range(self.REPEATS):
            x = self._double_round(x)
        output = [(self.state[i] + x[i]) & 0xffffffff for i in range(16)]
        return struct.pack('<16I', *output)

    def encrypt_block(self, block):
        if len(block) != 64:
            raise ValueError('Input data must be exactly 64 bytes')
        keystream = self._salsa20_block()
        self.state[8] = (self.state[8] + 1) & 0xffffffff
        if self.state[8] == 0:
            self.state[9] = (self.state[9] + 1) & 0xffffffff
        return bytes(a ^ b for a, b in zip(block, keystream))

    def encrypt(self, data):
        """
        Encrypts data by XORing with the keystream generated by Salsa20.
        This is reused to decrypt the data as well
        """
        encrypted_data = bytearray()
        while data:
            block = data[:64]
            data = data[64:]
            if len(block) < 64:
                block += b'\x00' * (64 - len(block))  # Pad to 64 bytes
            encrypted_data.extend(self.encrypt_block(block))
        return bytes(encrypted_data)

    def decrypt(self, encrypted_data):
        """
        Decrypts data by calling encrypt function (as salsa20's encryption is symmetric).
        Then converts the returned byte string into a string
        """
        byte_str = self.encrypt(encrypted_data)
        # l1 = byte_str.split("'")
        s1 = str(byte_str)
        # print(s1)
        l2 = s1.split('\\x00')
        ans = ""
        for a in l2:
            ans += a
        return l2[0][2:]
        # pass


def salsa20_encrypt_decrypt(key: bytes, nonce: bytes, message: bytes, is_true=True):
    """
    Made to test...
    """
    salsa20 = Salsa20(key, nonce)
    if is_true:
        return salsa20.encrypt(message)
    byte_str = salsa20.encrypt(message)
    # l1 = byte_str.split("'")
    s1 = str(byte_str)
    l2 = s1.split('\\x00')
    ans = ""
    for a in l2:
        ans += a
    return l2[0][2:]


# Test the implementation
def test_salsa20():
    key = b'\x01' * 32  # 256-bit key (all zeroes)
    nonce = b'\x00' * 8  # 64-bit nonce (all zeroes)
    # takes the message from a file (somefile.txt in this case)
    with open('somefile.txt') as file:
        s0 = file.read()
    s1 = s0.encode('utf-8')
    message = s1  # Message to encrypt

    print(f"Original Message: {message}")

    # Encrypt the message
    salsa20 = Salsa20(key, nonce)
    encrypted_message = salsa20.encrypt(message)
    print(f"Encrypted Message: {encrypted_message}")

    with open('somefile.txt', 'wb') as fole:
        fole.write(encrypted_message)

    with open('somefile.txt', 'rb') as f_in:
        encm = f_in.read()

    salsa20 = Salsa20(key, nonce)
    # Decrypt the message (Salsa20 encryption is symmetric)
    decrypted_message = salsa20.decrypt(encm)
    print(f"Decrypted Message: {decrypted_message}")


if __name__ == '__main__':
    test_salsa20()
