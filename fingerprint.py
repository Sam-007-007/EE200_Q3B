import pickle
with open("database.pkl","rb") as f:
    database = pickle.load(f)

def compute_spectrogram(signal, fs):

    f, t, Sxx = spectrogram(
        signal,
        fs=fs,
        nperseg=2048,
        noverlap=1024
    )

    Sxx_db = 10*np.log10(Sxx + 1e-10)

    return f, t, Sxx_db

def get_peaks(Sxx_db,
              neighborhood_size=20,
              threshold_percentile=95):

    local_max = maximum_filter(
        Sxx_db,
        size=neighborhood_size
    )

    peaks = (Sxx_db == local_max)

    threshold = np.percentile(
        Sxx_db,
        threshold_percentile
    )

    peaks &= (Sxx_db > threshold)

    freq_idx, time_idx = np.where(peaks)

    return list(zip(freq_idx, time_idx))

def generate_hashes(peaks, fan_value=10):

    hashes = []

    peaks = sorted(peaks, key=lambda x: x[1])

    for i in range(len(peaks)):

        f1, t1 = peaks[i]

        for j in range(1, fan_value):

            if i + j >= len(peaks):
                break

            f2, t2 = peaks[i+j]

            dt = t2 - t1

            if dt > 0:

                h = hash((f1, f2, dt))

                hashes.append((h, t1))

    return hashes

def identify_song(query_file):

    x, fs = librosa.load(
        query_file,
        sr=None,
        mono=True
    )

    f, t, Sxx_db = compute_spectrogram(x, fs)

    peaks = get_peaks(Sxx_db)

    hashes = generate_hashes(peaks)

    offsets = defaultdict(list)

    for h, t_query in hashes:

        if h in database:

            for song, t_song in database[h]:

                offsets[song].append(
                    t_song - t_query
                )

    scores = {}

    for song, offset_list in offsets.items():

        if len(offset_list)==0:
            continue

        count = Counter(offset_list)

        scores[song] = count.most_common(1)[0][1]

    if len(scores)==0:
        return None

    best_song = max(scores,key=scores.get)

    return (
        best_song,
        Sxx_db,
        peaks,
        offsets[best_song]
    )


