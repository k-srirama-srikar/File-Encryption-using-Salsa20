# File Encryption using a custom implementation of Salsa20


## About the project
 I've tried to implement Salsa20, a symmetric stream cipher, using python and then used it to encrypt or decrypt a text file.


## How to use
Before you try to run the program, make sure `PyQt` is installed \

Linux:
```bash
$ sudo apt-get install python3-pyqt5
```
Windows:
```bash
$ pip install PyQt5
```
You can now run the `main.py`, which will open a very minimalistic PyQt window like the one below \
![image](https://github.com/user-attachments/assets/af446f4c-28d5-4701-aa7a-9b62cbb31cd6) \
You can enter a password and select a text file to encrypt, which will create a `.txt.enc` file which will contain the encrypted text \
You can also decrypt it similarly by reentering the password and selecting the `.txt.enc` file which will give a `.txt.dec` file which contains the plain text\
You can try out the `test.txt` here and check how it works. \
Note that a `password_and_nonce.json` file will be created in the process of entering the password while encrypting. \
 


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
