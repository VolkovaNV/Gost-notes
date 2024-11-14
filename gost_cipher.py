def pad(data: bytes) -> bytes:
    padding_len = 8 - (len(data) % 8)
    return data + bytes([padding_len] * padding_len)

def nePad(data: bytes) -> bytes:
    padding_len = data[-1]
    return data[:-padding_len]

def rol(value: int, shift: int) -> int:
    return ((value << shift) & 0xFFFFFFFF) | (value >> (32 - shift))

sBlocks = [
    [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11], [7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3],
    [4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3], [13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12],
    [6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2], [14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9],
    [4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14], [1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 14, 3, 11, 6, 8, 12]
]

def substitute(value: int) -> int:
    result = 0
    for i in range(8):
        s_block = sBlocks[i][(value >> (4 * i)) & 0xF]
        result |= s_block << (4 * i)
    return result

def gostZah(text: bytes, key: bytes) -> bytes:
    text = pad(text)
    zahMsg = b''
    for i in range(0, len(text), 8):
        block = text[i:i+8]
        zahMsg += gostZah_block(block, key)
    return zahMsg

def gostRah(zahMsg: bytes, key: bytes) -> bytes:
    rahMsg = b''
    for i in range(0, len(zahMsg), 8):
        block = zahMsg[i:i+8]
        rahMsg += gostRah_block(block, key)
    return nePad(rahMsg)

def gostround(left: int, right: int, key: int) -> (int, int):
    temp = (left + key) % (2 ** 32)
    temp = substitute(temp)
    temp = rol(temp, 11)
    new_right = right ^ temp
    return new_right, left

def gostZah_block(block: bytes, key: bytes) -> bytes:
    left = int.from_bytes(block[:4], byteorder='little')
    right = int.from_bytes(block[4:], byteorder='little')
    key_parts = [int.from_bytes(key[i:i+4], byteorder='little') for i in range(0, 32, 4)]
    for i in range(24):
        right, left = gostround(left, right, key_parts[i % 8])
    for i in range(8):
        right, left = gostround(left, right, key_parts[7 - i])
    return left.to_bytes(4, byteorder='little') + right.to_bytes(4, byteorder='little')

def gostRah_block(block: bytes, key: bytes) -> bytes:
    left = int.from_bytes(block[:4], byteorder='little')
    right = int.from_bytes(block[4:], byteorder='little')
    key_parts = [int.from_bytes(key[i:i+4], byteorder='little') for i in range(0, 32, 4)]
    for i in range(8):
        right, left = gostround(left, right, key_parts[i])
    for i in range(24):
        right, left = gostround(left, right, key_parts[7 - (i % 8)])
    return left.to_bytes(4, byteorder='little') + right.to_bytes(4, byteorder='little')

# Example usage:
def encrypt_message(message: str, key: str) -> str:
    return gostZah(message.encode(), key.encode()).hex()

def decrypt_message(encrypted_message: str, key: str) -> str:
    return gostRah(bytes.fromhex(encrypted_message), key.encode()).decode()

if __name__ == '__main__':
    msg1 = encrypt_message('Lorem ipsum dolor sit, amet consectetur adipisicing elit. Nisi laudantium veritatis sed, fugiat laboriosam sequi quo officia neque aspernatur ipsum nam facilis, at, dolore quis corporis excepturi? Minima, corporis quae.', 'key')
    print(msg1)