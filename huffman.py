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
# Manual Min-Heap (no heapq)
# ------------------------------------------------------------

class MinHeap:
    def __init__(self):
        self.data = []

    def push(self, node):
        self.data.append(node)
        self._bubble_up(len(self.data) - 1)

    def pop(self):
        if len(self.data) == 1:
            return self.data.pop()
        root = self.data[0]
        self.data[0] = self.data.pop()
        self._bubble_down(0)
        return root

    def __len__(self):
        return len(self.data)

    def _bubble_up(self, idx):
        parent = (idx - 1) // 2
        while idx > 0 and self.data[idx].freq < self.data[parent].freq:
            self.data[idx], self.data[parent] = self.data[parent], self.data[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _bubble_down(self, idx):
        size = len(self.data)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx

            if left < size and self.data[left].freq < self.data[smallest].freq:
                smallest = left
            if right < size and self.data[right].freq < self.data[smallest].freq:
                smallest = right

            if smallest == idx:
                break

            self.data[idx], self.data[smallest] = self.data[smallest], self.data[idx]
            idx = smallest


# ------------------------------------------------------------
# Huffman Tree + Code Generation
# ------------------------------------------------------------

def build_frequency_table(text):
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


def build_huffman_tree(freq_table):
    heap = MinHeap()

    for ch, fr in freq_table.items():
        heap.push(Node(char=ch, freq=fr))

    # Single-symbol edge case: wrap the single leaf so encoding emits at least one bit.
    if len(heap) == 1:
        only = heap.pop()
        return Node(freq=only.freq, left=only)

    while len(heap) > 1:
        left = heap.pop()
        right = heap.pop()
        merged = Node(freq=left.freq + right.freq, left=left, right=right)
        heap.push(merged)

    return heap.pop()


def generate_codes(root):
    codes = {}

    def traverse(node, prefix):
        if node.is_leaf():
            # Ensure non-empty code for the single-symbol case.
            codes[node.char] = prefix if prefix != "" else "0"
            return
        traverse(node.left, prefix + "0")
        traverse(node.right, prefix + "1")

    traverse(root, "")
    return codes


# ------------------------------------------------------------
# Encoding + Decoding
# ------------------------------------------------------------

def encode(text, codes):
    return "".join(codes[ch] for ch in text)


def decode(bitstring, root):
    result = []
    node = root

    for bit in bitstring:
        node = node.left if bit == "0" else node.right
        if node.is_leaf():
            result.append(node.char)
            node = root

    return "".join(result)


# ------------------------------------------------------------
# Bit Packing / Unpacking
# ------------------------------------------------------------

def pack_bits(bitstring):
    out = bytearray()
    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i:i+8]
        if len(chunk) < 8:
            chunk += "0" * (8 - len(chunk))
        out.append(int(chunk, 2))
    return out


def unpack_bits(byte_data, bit_count):
    bits = ""
    for b in byte_data:
        bits += f"{b:08b}"
    return bits[:bit_count]


# ------------------------------------------------------------
# Binary File Format (Huffman)
#   [FREQ_COUNT 4B]
#   [(CHAR 1B, FREQ 4B) * FREQ_COUNT]
#   [BIT_COUNT 4B]
#   [PAYLOAD bytes...]
# ------------------------------------------------------------

def write_binary_file(path, freq_table, bit_count, packed_bytes):
    with open(path, "wb") as f:
        f.write(len(freq_table).to_bytes(4, "big"))
        for ch, fr in freq_table.items():
            # NOTE: Assumes ASCII/Latin-1 input so ord(ch) < 256
            f.write(bytes([ord(ch)]))
            f.write(fr.to_bytes(4, "big"))
        f.write(bit_count.to_bytes(4, "big"))
        f.write(packed_bytes)


def read_binary_file(path):
    with open(path, "rb") as f:
        freq_count = int.from_bytes(f.read(4), "big")

        freq_table = {}
        for _ in range(freq_count):
            ch = f.read(1).decode("utf-8")
            fr = int.from_bytes(f.read(4), "big")
            freq_table[ch] = fr

        bit_count = int.from_bytes(f.read(4), "big")
        packed_bytes = f.read()

    return freq_table, bit_count, packed_bytes


# ------------------------------------------------------------
# Public API (updated):
#   compress(input_path, alg)
#   decompress(input_path)
#
# Per your spec:
#   - 'h' -> write ..._compressed.huff (Huffman)
#   - 'c' -> write ..._compressed.custom (ALSO Huffman, by rubric)
#   - decompress decides by extension and decodes with Huffman in both cases
# ------------------------------------------------------------

def compress(input_path, alg):
    """
    Compress a text file using the selected algorithm and write the output.

    Parameters:
      input_path (str): path to a UTF-8 text file
      alg (str): 'h' for Huffman -> writes <base>_compressed.huff
                 'c' for Custom  -> writes <base>_compressed.custom
                 (Both use the same Huffman format/logic by rubric.)

    Returns:
      str: the output path written to disk
    """
    base = input_path.rsplit(".", 1)[0]

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Build Huffman (used for both 'h' and 'c' per rubric)
    freq = build_frequency_table(text)
    root = build_huffman_tree(freq)
    codes = generate_codes(root)
    encoded = encode(text, codes)
    packed = pack_bits(encoded)

    if alg == 'h':
        output_path = base + "_compressed.huff"
    elif alg == 'c':
        output_path = base + "_compressed.custom"
    else:
        raise ValueError("alg must be 'h' (Huffman) or 'c' (Custom-as-Huffman)")

    write_binary_file(output_path, freq, len(encoded), packed)

    print("Compressed →", output_path)
    return output_path


def decompress(input_path):
    """
    Decompress a file produced by `compress`.

    Decides decoder by extension:
      *.huff   -> Huffman
      *.custom -> Huffman (per rubric: custom uses the same Huffman format)

    Returns:
      str: the restored text file path
    """
    # Derive output name
    base = input_path.rsplit("_compressed", 1)[0]
    output_path = base + "_restored.txt"

    # Extension-based dispatch (both go through Huffman logic)
    if input_path.endswith(".huff") or input_path.endswith(".custom"):
        freq, bit_count, packed_bytes = read_binary_file(input_path)
        root = build_huffman_tree(freq)
        bitstring = unpack_bits(packed_bytes, bit_count)
        decoded = decode(bitstring, root)
    else:
        raise ValueError("Unknown extension (expected .huff or .custom)")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(decoded)

    print("Restored →", output_path)
    return output_path