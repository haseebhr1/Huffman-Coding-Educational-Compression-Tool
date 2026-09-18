# Huffman Coding Educational Compression Tool

An educational, pure-Python implementation of lossless Huffman text compression. The project demonstrates how character frequencies become a binary Huffman tree, how variable-length codes are generated, and how the resulting bitstream is packed into a custom binary file format.

## Project overview

The tool is designed to make the compression pipeline visible and approachable. It implements the core data structures and algorithms directly instead of relying on Python's `heapq` module or a third-party compression library.

### Key features

- Character-frequency analysis
- Manual min-heap implementation
- Huffman tree construction and traversal
- Prefix-free binary code generation
- Bitstring encoding and decoding
- Byte packing with explicit bit-count tracking
- Self-contained binary files with frequency-table metadata
- Lossless decompression and restored-text output
- Single-symbol input handling
- Sample input, compressed, and restored files for comparison

## How Huffman coding works

1. Count the frequency of each character in the input text.
2. Insert each character into a min-heap ordered by frequency.
3. Repeatedly combine the two least-frequent nodes to build the tree.
4. Traverse left and right branches to assign `0` and `1` codes.
5. Replace each input character with its Huffman code.
6. Pack the resulting bits into bytes and write the metadata and payload.
7. Rebuild the tree from the stored frequency table to decode the payload.

## Binary file format

The generated `.huff` and `.custom` files use the following layout:

```text
[frequency-entry count: 4 bytes]
[(character: 1 byte, frequency: 4 bytes) repeated]
[encoded bit count: 4 bytes]
[packed payload bytes]
```

The exact encoded bit count is stored because the final payload byte may contain padding bits.

## Usage

The public API is defined in `huffman.py`:

```python
import huffman

compressed_path = huffman.compress("test1.txt", "h")
restored_path = huffman.decompress(compressed_path)

print(compressed_path)  # test1_compressed.huff
print(restored_path)    # test1_restored.txt
```

The algorithm argument supports two output extensions:

| Argument | Output | Decoder |
| --- | --- | --- |
| `"h"` | `<base>_compressed.huff` | Huffman |
| `"c"` | `<base>_compressed.custom` | Huffman-compatible custom path |

Both paths use the Huffman format and implementation required by the assignment specification.

## Running a round-trip example

From the project directory:

```powershell
python -c "import huffman; p = huffman.compress('test1.txt', 'h'); print('Compressed:', p); print('Restored:', huffman.decompress(p))"
```

The repository includes `test1.txt`, `test2.txt`, their compressed outputs, and restored copies that can be used to compare the original and decompressed text.

## Repository layout

- `huffman.py` — completed Huffman compressor/decompressor
- `huffman_skeleton.py` — instructional starter file with implementation points marked
- `huffman_test.py` — timing, size, compression-ratio, and round-trip test scaffold
- `test1.txt`, `test2.txt` — sample input files
- `*_compressed.huff` — sample binary Huffman outputs
- `*_restored.txt` — sample decompressed outputs

## Concepts demonstrated

This project applies priority queues, binary trees, recursion, prefix codes, bit-level representation, binary file I/O, algorithmic complexity, and lossless data verification. It is intended for educational text compression and uses a one-byte character entry in its file metadata.
