#!/usr/bin/env python3
import re
import argparse
from ctypes import windll, c_char_p, c_void_p, cast, CFUNCTYPE, byref, c_uint32

# Configuration
XOR_KEY = 0xAA  # XOR key for encoding (optional)
OUTPUT_FILE = "shellcode.bin"  # Default output file

def xor_encode(shellcode, key=XOR_KEY):
    """XOR-encode shellcode to avoid null bytes."""
    return bytes([b ^ key for b in shellcode])

def parse_objdump_output(objdump_file):
    """
    Parses objdump output (e.g., `objdump -D -M intel <file>`).
    Extracts opcodes and handles assembly comments.
    """
    shellcode = bytearray()
    with open(objdump_file, 'r') as f:
        for line in f:
            # Match lines like: "  401000:       c3                      ret"
            match = re.search(r'^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s)+)', line)
            if match:
                opcodes = match.group(1).strip().split()
                shellcode.extend(int(op, 16) for op in opcodes)
    return bytes(shellcode)

def format_shellcode(shellcode, format_type="c", bytes_per_line=16):
    """
    Formats shellcode for C or Python.
    - `format_type`: "c" or "python"
    """
    formatted = []
    for i in range(0, len(shellcode), bytes_per_line):
        chunk = shellcode[i:i+bytes_per_line]
        hex_str = "".join([f"\\x{b:02x}" for b in chunk])
        if format_type == "c":
            formatted.append(f'"{hex_str}"')
        else:
            formatted.append(f'buf += b"{hex_str}"')
    return "\n".join(formatted)

def write_shellcode_to_file(shellcode, filename):
    """Writes raw shellcode to a binary file."""
    with open(filename, "wb") as f:
        f.write(shellcode)
    print(f"[+] Raw shellcode saved to: {filename}")

def test_shellcode(shellcode):
    """Executes shellcode in memory (for testing)."""
    try:
        ptr = windll.kernel32.VirtualAlloc(
            None,
            len(shellcode),
            0x1000,  # MEM_COMMIT
            0x40     # PAGE_EXECUTE_READWRITE
        )
        if not ptr:
            print("[!] Failed to allocate memory")
            return False

        windll.kernel32.RtlMoveMemory(ptr, shellcode, len(shellcode))
        windll.kernel32.FlushInstructionCache(windll.kernel32.GetCurrentProcess(), ptr, len(shellcode))

        func_type = CFUNCTYPE(None)
        func = cast(ptr, func_type)
        print("[+] Executing shellcode...")
        func()

        windll.kernel32.VirtualFree(ptr, 0, 0x8000)  # MEM_RELEASE
        return True
    except Exception as e:
        print(f"[!] Shellcode execution failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert objdump output to shellcode (raw/C/Python).")
    parser.add_argument("objdump_file", help="Path to objdump output file")
    parser.add_argument("--output", help="Output .bin file (default: shellcode.bin)", default=OUTPUT_FILE)
    parser.add_argument("--format", help="Output format: c (default) or python", default="c")
    parser.add_argument("--xor", help="Enable XOR encoding", action="store_true")
    parser.add_argument("--test", help="Test shellcode execution", action="store_true")
    args = parser.parse_args()

    # Parse objdump output
    shellcode = parse_objdump_output(args.objdump_file)
    if not shellcode:
        print("[!] No shellcode extracted")
        return

    print(f"[+] Shellcode size: {len(shellcode)} bytes")

    # XOR encode if requested
    if args.xor:
        print(f"[+] XOR-encoding shellcode (key=0x{XOR_KEY:02x})")
        shellcode = xor_encode(shellcode)

    # Write raw shellcode
    write_shellcode_to_file(shellcode, args.output)

    # Print formatted shellcode
    print(f"\n// --- {args.format.upper()} Shellcode (16-byte chunks) ---")
    print(format_shellcode(shellcode, args.format))

    # Test if requested
    if args.test:
        print("\n[+] Testing shellcode...")
        if not test_shellcode(shellcode):
            print("[!] Shellcode test failed (check debugger)")

if __name__ == "__main__":
    main()
