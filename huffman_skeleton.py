# ============================================================
# Lossless Text Compression (Skeleton)
# - Pure Python (NO imports)
# - 'h' -> <base>_compressed.huff   (Huffman)
# - 'c' -> <base>_compressed.custom (Custom, but also Huffman by rubric)
# - Decompression chooses by extension (.huff or .custom)
# - Text-only (UTF-8)
# ============================================================

# ------------------------------------------------------------
# Huffman Tree Node
# ------------------------------------------------------------

class Node:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


# ------------------------------------------------------------
# Manual Min-Heap (no heapq) — SKELETON
#   Students must implement a min-heap of Node by node.freq
# ------------------------------------------------------------

class MinHeap:
    def __init__(self):
        self.data = []

    def push(self, node):
        """Insert a Node and restore heap property."""
        raise NotImplementedError

    def pop(self):
        """Remove and return the Node with minimum freq."""
        raise NotImplementedError

    def __len__(self):
        """Return number of elements in the heap."""
        return len(self.data)

    # Optional internal helpers (students implement as needed)
    def _bubble_up(self, idx):
        raise NotImplementedError

    def _bubble_down(self, idx):
        raise NotImplementedError


# ------------------------------------------------------------
# Huffman: Frequency, Tree, Codes — SKELETON
# ------------------------------------------------------------

def build_frequency_table(text):
    """Return dict: char -> frequency."""
    raise NotImplementedError


def build_huffman_tree(freq_table):
    """Return root Node of Huffman tree. Handle single-symbol input."""
    raise NotImplementedError


def generate_codes(root):
    """
    Return dict: char -> code ('0'/'1').
    Ensure non-empty code for single-symbol input (e.g., use '0').
    """
    raise NotImplementedError


# ------------------------------------------------------------
# Encode / Decode — SKELETON
# ------------------------------------------------------------

def encode(text, codes):
    """Return bitstring ('0'/'1') for text using codes."""
    raise NotImplementedError


def decode(bitstring, root):
    """Return original text decoded from bitstring using Huffman tree."""
    raise NotImplementedError


# ------------------------------------------------------------
# Bit Packing / Unpacking — SKELETON
# ------------------------------------------------------------

def pack_bits(bitstring):
    """Return bytes from a '0'/'1' bitstring (pad final byte with zeros)."""
    raise NotImplementedError


def unpack_bits(byte_data, bit_count):
    """Return first bit_count bits as a '0'/'1' string from bytes."""
    raise NotImplementedError


# ------------------------------------------------------------
# Binary File Format (Huffman for BOTH .huff and .custom)
#   [FREQ_COUNT 4B]
#   [(CHAR 1B, FREQ 4B) * FREQ_COUNT]  # ASCII/Latin-1 only
#   [BIT_COUNT 4B]
#   [PAYLOAD bytes...]
# ------------------------------------------------------------

def write_binary_file(path, freq_table, bit_count, packed_bytes):
    """Write Huffman binary format to path."""
    raise NotImplementedError


def read_binary_file(path):
    """Return (freq_table, bit_count, packed_bytes) read from path."""
    raise NotImplementedError


# ------------------------------------------------------------
# Public API
#   compress(input_path, alg)  -> writes file, returns output path
#   decompress(input_path)     -> writes file, returns output path
#
# Rules:
#   - 'h' -> <base>_compressed.huff
#   - 'c' -> <base>_compressed.custom  (custom uses Huffman too)
#   - decompress decides by extension (.huff or .custom) and decodes via Huffman
# ------------------------------------------------------------

def compress(input_path, alg):
    """
    Compress UTF-8 text at input_path using algorithm 'h' or 'c'.
    Writes:
      - 'h' -> <base>_compressed.huff
      - 'c' -> <base>_compressed.custom
    Returns written output path.
    """
    base = input_path.rsplit(".", 1)[0]
    if alg == 'h':
        output_path = base + "_compressed.huff"
    elif alg == 'c':
        output_path = base + "_compressed.custom"
    else:
        raise ValueError("alg must be 'h' or 'c'")

    f = open(input_path, "r", encoding="utf-8")
    text = f.read()
    f.close()

    # BOTH paths use Huffman (per rubric)
    freq = build_frequency_table(text)
    root = build_huffman_tree(freq)
    codes = generate_codes(root)
    bitstring = encode(text, codes)
    packed = pack_bits(bitstring)
    write_binary_file(output_path, freq, len(bitstring), packed)

    return output_path


def decompress(input_path):
    """
    Decompress file produced by compress(). Uses extension to choose:
      - .huff   -> Huffman
      - .custom -> Huffman (custom path uses same format)
    Writes:
      <base>_restored.txt
    Returns written output path.
    """
    if not (input_path.endswith(".huff") or input_path.endswith(".custom")):
        raise ValueError("Unknown extension (expected .huff or .custom)")

    base = input_path.rsplit("_compressed", 1)[0]
    output_path = base + "_restored.txt"

    freq, bit_count, packed_bytes = read_binary_file(input_path)
    root = build_huffman_tree(freq)
    bitstring = unpack_bits(packed_bytes, bit_count)
    text = decode(bitstring, root)

    g = open(output_path, "w", encoding="utf-8")
    g.write(text)
    g.close()

    return output_path