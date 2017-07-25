import map

encoding    = 'ascii'
edian       = 'little'
replacement = '?'.encode(encoding)
codepage    = 0

def enc(txt):
    if isinstance(txt, str):
        return txt.encode(encoding)
    elif isinstance(txt, bytes):
        return txt
    else:
        return txt.to_bytes(1, edian)

def char_encode(char):
    cp = ord(char)
    if cp < 80:
        return char.encode(encoding)
    elif cp in map.chars:
        page, pos = map.chars[cp]
        if page == codepage:
            return enc(pos)
        else:
            return b'\x1b\x74' + enc(page) + enc(pos)
    else:
        return replacement

def encode(txt):
    # start out at cp0
    codepage = 0
    msg = b'\x1b\x74\x00'
    for c in txt:
        msg += char_encode(c)
    return msg
