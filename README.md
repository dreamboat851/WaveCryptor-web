# WebCryptor
WebCryptor is an innovative web app that securely encodes and encrypts messages into audio files. Utilizing Streamlit for a user-friendly interface, WebCryptor enables users to encode messages as composite audio signals and encrypts frequency mappings with an AES encryption key. The app also offers a streamlined decoding process, which reconstructs the original message using the audio file, frequency key, and encryption key.

# Key Features
## Message Encoding to Audio:
Transforms text messages into audio signals using dynamically allocated frequencies for each character.
## AES Encryption: 
Secures the frequency map and unused frequencies with a generated AES encryption key.
## Comprehensive Decoding: 
Decodes the message with high accuracy, requiring the audio file, frequency key, and encryption key.
## One-Click Download: 
Users can easily download the encoded audio, frequency key, and encryption key files as a zip.

# Technologies Used
Streamlit: For interactive and easy-to-use web deployment.
NumPy & SciPy: For signal processing and audio manipulation.
Cryptography: For AES-based encryption to securely encode frequency mappings.
# Setup
Clone the repository, install dependencies with requirements.txt, and deploy on Heroku or locally to transform your messages into secure, shareable audio files.
