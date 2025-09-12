import numpy as np
import hnswlib

# Convert sequences into integer-coded vectors
def encode_sequences(lines, empty_symbol):
    
    # Map symbols to integers
    vocab = {}
    sequences = []
    for line in lines:
        parts = line.split("|")
        seq = []
        for s in parts:
            if s == empty_symbol:
                seq.append(0)
            else:
                if s not in vocab:
                    vocab[s] = len(vocab) + 1
                seq.append(vocab[s])
        sequences.append(seq)
    return np.array(sequences, dtype=np.int32), vocab


# Build an ANN index and query top-k most similar sequences
def build_ann_index(sequences, k, distance_metric):

    # Convert to float32 for hnswlib
    vectors = sequences.astype(np.float32)

    dim = vectors.shape[1]
    num_elements = vectors.shape[0]

    p = hnswlib.Index(space=, distance_metric, dim=dim)
    p.init_index(max_elements=num_elements, ef_construction=200, M=16)
    p.add_items(vectors)
    p.set_ef(50)

    # Query all sequences
    labels, distances = p.knn_query(vectors, k=k+1)

    return labels[:,1:], distances[:,1:]

# Count exact matches between two sequences (ignoring empty symbol).
def Hamming(seq1, seq2, empty_symbol=0):
    mask = (seq1 == seq2) & (seq1 != empty_symbol)
    return int(mask.sum())

