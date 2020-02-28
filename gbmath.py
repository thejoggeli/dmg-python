def signed_byte(unsigned_byte):
    if(unsigned_byte > 127):
        return unsigned_byte-256
    return unsigned_byte