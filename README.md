# File Encryption using a custom implementation of Salsa20


## About the project
 I've tried to implement Salsa20, a symmetric stream cipher, using python and then used it to encrypt or decrypt a text file.


## How to use?
Before you try to run the program, make sure `PyQt` is installed 

Linux:
```bash
$ sudo apt-get install python3-pyqt5
```
Windows:
```shell
$ pip install PyQt5
```
You can now run the `main.py`, which will open a very minimalistic PyQt window like the one below \
![image](https://github.com/user-attachments/assets/af446f4c-28d5-4701-aa7a-9b62cbb31cd6) \
You can enter a password and select a text file to encrypt, which will create a `.txt.enc` file which will contain the encrypted text. \
You can also decrypt it similarly by reentering the password and selecting the `.txt.enc` file which will give a `.txt.dec` file which contains the plain text.\
You can try out the `test.txt` here and check how it works. 
> [!NOTE]
> A `password_and_nonce.json` file will be created in the process of entering the password while encrypting. 
 

## How does the program work?

### Working of `main.py`
`main.py` is a PyQt5-based graphical user interface (GUI) application that allows users to encrypt and decrypt files using the Salsa20 encryption algorithm. The program takes a user-provided password, derives a cryptographic key from it, and uses this key to encrypt/decrypt a file. A nonce (number used once) is used to ensure that the encryption is secure, even if the same password is used multiple times.

**Program Flow:**

The user selects a file and provides a password.

If encrypting, the program generates a nonce, checks if it's been used before, derives a key from the password, and encrypts the file.

If decrypting, the program retrieves the nonce from a JSON file, derives the key, and decrypts the file.

The GUI gives feedback to the user through dialogs.


__Components:__

1. _Key Derivation_ (`derive_key`):

The program takes a password and uses the SHA-256 hashing function to generate a 256-bit key (or 32 bytes). This key will be used in the Salsa20 encryption algorithm.



2. _Nonce Generation_ (`generate_nonce`):

A nonce (random 8-byte sequence) is generated using `os.urandom(8)` and ensures that even if the same password is reused, the encryption is different each time.



3. _Nonce Checking and Storage_ (`check_nonce`):

The nonce is stored in a JSON file (`password_and_nonce.json`) along with the password, encoded in Base64 format. This file ensures that nonces are not reused. If a nonce has been used before, the program generates a new one to avoid security issues with nonce reuse.



4. _File Encryption_ (`encrypt_file`):

The program reads a file, uses the derived key and generated nonce, and initializes the Salsa20 cipher. The file content is encrypted using Salsa20 and written into a new file with the `.enc` extension.

Before encryption, the program checks if the nonce has been used before and stores it in the JSON file.



5. _File Decryption_ (`decrypt_file`):

The decryption process reverses the encryption. The nonce is retrieved from the JSON file, the cipher is initialized with the key and nonce, and the encrypted content is decrypted back into its original form. The decrypted content is written into a new file with a `.dec` extension.



6. _PyQt5 GUI_ (`FileEncryptor` class):

A simple GUI allows users to input a password, select a file, and choose whether to encrypt or decrypt the file. The application provides feedback to the user through pop-up dialogs.


### Working of `salsa20.py`

`salsa20.py` implements the Salsa20 stream cipher from scratch in Python, supporting both 128-bit and 256-bit keys. The cipher is symmetric, meaning the same algorithm is used for both encryption and decryption.



**Program Flow:**

A custom implementation of Salsa20 is provided, including functions for key setup, nonce setup, and encryption/decryption.

The program reads a file, encrypts its contents using the Salsa20 algorithm, writes the encrypted data back to the file, and decrypts it to ensure correctness.


**Components:**

1. _Salsa20 Class Initialization_ (`__init__`):

The class constructor takes a key (either 16 bytes for 128-bit encryption or 32 bytes for 256-bit encryption) and a nonce (8 bytes).

It initializes the internal state of the cipher, which is a 16-element array based on the key, nonce, and constants (TAU for 128-bit keys and SIGMA for 256-bit keys).



2. _Quarter-Round, Row-Round, and Column-Round Functions_:

Salsa20 works by applying a series of transformations on the state, consisting of "quarter rounds" that involve bitwise rotations and additions. These rounds are combined into row and column operations to mix the data thoroughly.



3. _Double Round and Salsa20 Block_ (`_salsa20_block`):

The double round function applies the row and column transformations. After repeating these rounds 20 times, the resulting state is used to generate a 64-byte keystream block.

The keystream block is XORed with a 64-byte data block (the message) to produce the encrypted output.



4. _Encrypting and Decrypting Blocks_ (`encrypt_block`):

The program encrypts 64-byte blocks of data by XORing them with the keystream generated by Salsa20. The same function is used for decryption since Salsa20 is symmetric (encryption and decryption are identical).



5. _Encrypting and Decrypting Data_ (`encrypt`, `decrypt`):

The encrypt function splits the input data into 64-byte blocks and encrypts each block. The decrypt function works similarly, as encryption and decryption are identical in a stream cipher like Salsa20.

The output is a byte stream of encrypted or decrypted data.



6. _Testing the Cipher_ (`test_salsa20`):

The test function reads a message from a file (`somefile.txt`), encrypts it using Salsa20, writes the encrypted data back to the file, and then decrypts it. The decrypted data is printed to verify that it matches the original message.



## About Salsa20
Salsa20 is a stream cipher designed by Daniel J. Bernstein. It's known for its efficiency and security and is used to encrypt data by generating a pseudorandom keystream that is XORed with the plaintext. Here's a high-level overview:

### Structure of Salsa20

1. **State Array**:
   Salsa20 operates on a 4x4 array of 32-bit words, totaling 128 bits of state. The state is initialized with a 256-bit key, a 64-bit nonce (also known as a counter), and a 64-bit block counter.

2. **Key and Nonce**:
   - **Key**: 256 bits (32 bytes)
   - **Nonce**: 64 bits (8 bytes)

3. **Rounds**:
   Salsa20 performs a series of operations in a number of rounds to mix the state and produce the pseudorandom output. The standard Salsa20 uses 20 rounds, while a variant called Salsa20/12 uses 12 rounds for efficiency.

### Key Operations

1. **Quarter Round**:
   The quarter round is a fundamental operation in Salsa20. It updates four words of the state array using bitwise operations, additions, and XORs. The operations ensure that the final output is highly scrambled.

2. **Column Round**:
   The column round applies quarter rounds to the columns of the state array.

3. **Diagonal Round**:
   The diagonal round applies quarter rounds to the diagonals of the state array.

Below is the C++ implementation of the Salsa20 core:
```c++
#define R(a,b) (((a) << (b)) | ((a) >> (32 - (b))))
     void salsa20_word_specification(uint32 out[16],uint32 in[16])
     {
       int i;
       uint32 x[16];
       for (i = 0;i < 16;++i) x[i] = in[i];
       for (i = 20;i > 0;i -= 2) {
         x[ 4] ^= R(x[ 0]+x[12], 7);  x[ 8] ^= R(x[ 4]+x[ 0], 9);
         x[12] ^= R(x[ 8]+x[ 4],13);  x[ 0] ^= R(x[12]+x[ 8],18);
         x[ 9] ^= R(x[ 5]+x[ 1], 7);  x[13] ^= R(x[ 9]+x[ 5], 9);
         x[ 1] ^= R(x[13]+x[ 9],13);  x[ 5] ^= R(x[ 1]+x[13],18);
         x[14] ^= R(x[10]+x[ 6], 7);  x[ 2] ^= R(x[14]+x[10], 9);
         x[ 6] ^= R(x[ 2]+x[14],13);  x[10] ^= R(x[ 6]+x[ 2],18);
         x[ 3] ^= R(x[15]+x[11], 7);  x[ 7] ^= R(x[ 3]+x[15], 9);
         x[11] ^= R(x[ 7]+x[ 3],13);  x[15] ^= R(x[11]+x[ 7],18);
         x[ 1] ^= R(x[ 0]+x[ 3], 7);  x[ 2] ^= R(x[ 1]+x[ 0], 9);
         x[ 3] ^= R(x[ 2]+x[ 1],13);  x[ 0] ^= R(x[ 3]+x[ 2],18);
         x[ 6] ^= R(x[ 5]+x[ 4], 7);  x[ 7] ^= R(x[ 6]+x[ 5], 9);
         x[ 4] ^= R(x[ 7]+x[ 6],13);  x[ 5] ^= R(x[ 4]+x[ 7],18);
         x[11] ^= R(x[10]+x[ 9], 7);  x[ 8] ^= R(x[11]+x[10], 9);
         x[ 9] ^= R(x[ 8]+x[11],13);  x[10] ^= R(x[ 9]+x[ 8],18);
         x[12] ^= R(x[15]+x[14], 7);  x[13] ^= R(x[12]+x[15], 9);
         x[14] ^= R(x[13]+x[12],13);  x[15] ^= R(x[14]+x[13],18);
       }
       for (i = 0;i < 16;++i) out[i] = x[i] + in[i];
     }
```

### Process

1. **Key Expansion**:
   The key and nonce are used to initialize the state array. The 256-bit key is divided into the state matrix, and the nonce is used to set up the initial values for the counter.

2. **State Transformation**:
   Salsa20 applies the column and diagonal rounds to the state matrix. This involves a series of quarter rounds, ensuring that the state matrix becomes highly pseudorandom.

3. **Keystream Generation**:
   After transforming the state, Salsa20 outputs a 64-byte keystream block. This block is then XORed with the plaintext to produce the ciphertext. For decryption, the same keystream is XORed with the ciphertext to recover the plaintext.

### Security

Salsa20 is designed to be fast and secure. It has undergone extensive cryptanalysis and has been found to be resistant to known attacks when implemented correctly. The cipher is based on simple, well-understood operations and is suitable for both software and hardware implementations.

### Use Cases

Salsa20 is used in various applications, including:

- **Encryption**: For securing data in transit or at rest.
- **Random Number Generation**: As a component in cryptographic systems where random data is required.
- **File Formats and Protocols**: In formats and protocols where secure data encryption is needed.

Overall, Salsa20 is valued for its combination of speed, simplicity, and security, making it a popular choice for stream encryption in modern cryptographic applications.
### Refrences

This is the website of Salsa20 authored by the designer (Daniel J. Bernstein) : [Salsa20](https://cr.yp.to/salsa20.html)
