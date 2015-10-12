def unhexlify(hexstring):
    return bytearray.fromhex(hexstring.replace('\n', ''))
