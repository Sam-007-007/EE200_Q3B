import streamlit as st
import tempfile
import matplotlib.pyplot as plt

from fingerprint import identify_song

st.title("🎵 Song Identifier")

uploaded_file = st.file_uploader(
    "Upload an MP3 file",
    type=["mp3","wav"]
)

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(delete=False) as tmp:

        tmp.write(uploaded_file.read())

        filename = tmp.name

    result = identify_song(filename)

    if result is not None:

        song_name,Sxx_db,peaks,offsets_best = result

        st.success(
            "Recognized Song: "+song_name
        )

        # Spectrogram
        fig,ax = plt.subplots(figsize=(10,5))

        ax.imshow(
            Sxx_db,
            origin='lower',
            aspect='auto',
            cmap='inferno'
        )

        ax.set_title("Spectrogram")

        st.pyplot(fig)


        # Constellation map
        fig,ax = plt.subplots(figsize=(10,5))

        times = [p[1] for p in peaks]
        freqs = [p[0] for p in peaks]

        ax.scatter(
            times,
            freqs,
            s=2
        )

        ax.set_title("Constellation Map")

        st.pyplot(fig)


        # Histogram
        fig,ax = plt.subplots(figsize=(10,5))

        ax.hist(offsets_best,bins=100)

        ax.set_title("Offset Histogram")

        st.pyplot(fig)