import re

def extract_bytes_from_asm(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    # Extract all hex bytes (supports 0x77, 77, or 77h formats)
    byte_matches = re.findall(r'(?:0x|h)?([0-9a-fA-F]{2})\b', content)
    return bytes([int(b, 16) for b in byte_matches])

def format_hex_dump(raw_bytes):
    # Format like a hex dump (e.g., "77 30 00 00")
    return ' '.join([f'{byte:02x}' for byte in raw_bytes])

def generate_shellcode(raw_bytes):
    return ''.join([f'\\x{byte:02x}' for byte in raw_bytes])

# --- Main ---
input_file = "assembly.asm"  # Replace with your file
output_file = "shellcode.txt"

try:
    raw_bytes = extract_bytes_from_asm(input_file)
    hex_dump = format_hex_dump(raw_bytes)
    shellcode = generate_shellcode(raw_bytes)

    print(f"\nRaw Bytes (Hex):\n\n{hex_dump}\n")
    print(f"Shellcode Format:\n\n{shellcode}\n")

    with open(output_file, 'w') as f:
        f.write(shellcode)
    print(f"Shellcode saved to {output_file}")

except FileNotFoundError:
    print(f"Error: File '{input_file}' not found.")
except Exception as e:
    print(f"Error: {e}")
