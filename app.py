import streamlit as st
import numpy as np
from scipy.io import wavfile
from scipy.io.wavfile import write
import random
import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from io import BytesIO
import zipfile

# Streamlit configuration
st.set_page_config(page_title="WaveCryptor", page_icon="🔒", layout="wide")

# Custom CSS for Techno look
st.markdown("""
    <style>
    body {
        background-color: #0a0a0a !important;
        color: #00ffcc !important;
        font-family: 'Roboto', sans-serif;
    }
    .title {
        text-align: center;
        font-size: 3rem;
        color: #00ffcc;
        text-shadow: 
            1px 1px 2px #111,  
            -1px -1px 2px #111,  
            1px -1px 0 #111,  
            -1px 1px 0 #111,  
            0 0 25px #00ffcc, 
            0 0 5px #00ffcc; /* Embossed look with outer glowing effect */
        font-weight: bold;
    }
    .header {
        font-size: 2rem;
        color: #ff33cc;
        text-align: center;
        text-shadow: 
            1px 1px 2px #111,  
            -1px -1px 2px #111,  
            1px -1px 0 #111,  
            -1px 1px 0 #111,
            0 0 20px #ff33cc, 
            0 0 5px #ff33cc;
        font-weight: bold;
    }
    .section {
        border: 2px solid #00ffcc;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .section input, .section button, .section select {
        background-color: #111111 !important;
        color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
        font-size: 1rem;
    }
    .section button:hover {
        background-color: #00ffcc !important;
        color: #111111 !important;
    }
    .download-button {
        background-color: #00ffcc !important;
        color: #111111 !important;
        font-size: 1.2rem;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .download-button:hover {
        background-color: #ff33cc !important;
        color: #111111 !important;
    }
    </style>
""", unsafe_allow_html=True)


# Header
st.markdown("<h1 class='title'>WaveCryptor: Encrypt Your Secrets with Sound</h1>", unsafe_allow_html=True)
st.write("Welcome to **SonicVault**, a fun and secure way to send messages using sound frequencies! Use this app to encode your secret message, encrypt it, and listen to it as an audio file.")

# Frequency map generator
def dynamic_frequency_allocation():
    base_freq = np.random.randint(500, 1000)
    all_frequencies = [base_freq + i * 50 for i in range(76)]
    np.random.shuffle(all_frequencies)
    characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789. ")
    freq_map = {characters[i]: all_frequencies[i] for i in range(len(characters))}
    unused_freqs = all_frequencies[len(characters):]
    return freq_map, unused_freqs

# Create the audio file
def create_composite_wave(message, freq_map, unused_freqs, duration=0.5, sample_rate=44100):
    composite_wave = np.array([], dtype=np.float32)
    for char in message:
        if char in freq_map:
            freq = freq_map[char]
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave_segment = 0.5 * np.sin(2 * np.pi * freq * t)
            composite_wave = np.concatenate((composite_wave, wave_segment))
            if random.random() < 0.9 and unused_freqs:
                nothing_freq = random.choice(unused_freqs)
                wave_segment = 0.5 * np.sin(2 * np.pi * nothing_freq * t)
                composite_wave = np.concatenate((composite_wave, wave_segment))
    composite_wave = np.int16(composite_wave / np.max(np.abs(composite_wave)) * 32767)
    return composite_wave

# Encrypt frequency map
def encrypt_frequency_key_file(freq_map, unused_freqs, encryption_key):
    key_dict = {"freq_map": freq_map, "unused_freqs": unused_freqs}
    json_data = json.dumps(key_dict).encode('utf-8')
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(b'1234567890123456'), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

# Generate encryption key
def write_encryption_key():
    encryption_key = os.urandom(16)
    encoded_key = base64.b64encode(encryption_key).decode('utf-8')
    return encryption_key, encoded_key

# Decode the frequency map
def decrypt_frequency_key_file(encrypted_data, encryption_key):
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(b'1234567890123456'), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    json_data = unpadder.update(padded_data) + unpadder.finalize()
    key_data = json.loads(json_data)
    freq_map = {int(v): k for k, v in key_data["freq_map"].items()}
    unused_freqs = set(key_data["unused_freqs"])
    return freq_map, unused_freqs

# Detect and decode frequencies
def detect_frequencies(audio_data, freq_map, unused_freqs, segment_duration=0.5, sample_rate=44100, threshold=0.5):
    segment_size = int(segment_duration * sample_rate)
    num_segments = len(audio_data) // segment_size
    detected_message = []
    for i in range(num_segments):
        segment = audio_data[i * segment_size: (i + 1) * segment_size]
        fft_result = np.fft.fft(segment)
        freqs = np.fft.fftfreq(len(fft_result), 1 / sample_rate)
        magnitude = np.abs(fft_result)
        peak_freq = freqs[np.argmax(magnitude)]
        if peak_freq in freq_map:
            detected_character = freq_map[peak_freq]
            detected_message.append(detected_character)
    return ''.join(detected_message)

# Streamlit App
st.title("SonicVault: Message Encoder and Decoder")

# Encoding section
st.header("Encoding Section")
message = st.text_input("Enter the message to encode:")

if "buttons_shown" not in st.session_state:
    st.session_state.buttons_shown = False

# Encoding section
if st.button("Encode"):
    if message:
        freq_map, unused_freqs = dynamic_frequency_allocation()
        composite_wave = create_composite_wave(message.upper(), freq_map, unused_freqs)
        encryption_key, encoded_key = write_encryption_key()
        encrypted_freq_data = encrypt_frequency_key_file(freq_map, unused_freqs, encryption_key)

        # Create BytesIO for each file and ZIP
        wav_io = BytesIO()
        write(wav_io, 44100, composite_wave)
        wav_io.seek(0)

        freq_key_io = BytesIO(encrypted_freq_data)
        encryption_key_io = BytesIO(encoded_key.encode())

        # Create a ZIP file to bundle all files
        zip_io = BytesIO()
        with zipfile.ZipFile(zip_io, "w") as zip_file:
            zip_file.writestr("composite_message.wav", wav_io.getvalue())
            zip_file.writestr("frequency_key_encrypted.json", freq_key_io.getvalue())
            zip_file.writestr("encryption_key.key", encryption_key_io.getvalue())
        zip_io.seek(0)

        # Display a single download button for the ZIP file
        st.download_button("Download All Files", zip_io, "encoded_files.zip", "application/zip", key="download_zip_file")

    else:
        st.error("Please enter a message.")


# Keep buttons visible even if Encode is clicked
if st.session_state.buttons_shown:
    st.download_button("Download All Files", zip_io, "encoded_files.zip", "application/zip")

# Decoding section
st.header("Decoding Section")
uploaded_wav_file = st.file_uploader("Upload WAV file", type=["wav"])
uploaded_freq_key_file = st.file_uploader("Upload Frequency Key File", type=["json"])
uploaded_encryption_key_file = st.file_uploader("Upload Encryption Key File", type=["key"])

if st.button("Decode"):
    if uploaded_wav_file and uploaded_freq_key_file and uploaded_encryption_key_file:
        # Load encryption key
        encryption_key = base64.b64decode(uploaded_encryption_key_file.getvalue())
        
        # Load and decrypt frequency key file
        encrypted_freq_data = uploaded_freq_key_file.getvalue()
        freq_map, unused_freqs = decrypt_frequency_key_file(encrypted_freq_data, encryption_key)
        
        # Read WAV file
        sample_rate, audio_data = wavfile.read(uploaded_wav_file)
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Decode message
        decoded_message = detect_frequencies(audio_data, freq_map, unused_freqs, sample_rate=sample_rate)
        st.write("Decoded Message:", decoded_message)
    else:
        st.error("Please upload all required files.")
