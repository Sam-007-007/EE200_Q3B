import streamlit as st
import tempfile
import matplotlib.pyplot as plt
import pandas as pd
import os

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


st.header("Batch Mode")

batch_files = st.file_uploader(
    "Upload multiple audio clips",
    type=["mp3", "wav"],
    accept_multiple_files=True
)

if batch_files:

    results = []

    for uploaded_file in batch_files:

        with tempfile.NamedTemporaryFile(delete=False) as tmp:

            tmp.write(uploaded_file.read())
            filename = tmp.name

        result = identify_song(filename)

        if result is not None:

            song_name, _, _, _ = result

            # remove extension from prediction
            prediction = os.path.splitext(song_name)[0]

        else:

            prediction = "No Match"

        results.append(
            {
                "filename": uploaded_file.name,
                "prediction": prediction
            }
        )

    df = pd.DataFrame(results)

    st.write(df)

    csv = df.to_csv(index=False)

    st.download_button(
        label="Download results.csv",
        data=csv,
        file_name="results.csv",
        mime="text/csv"
    )