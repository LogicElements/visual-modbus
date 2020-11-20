
"""
Standard Ethernet CRC 32 polynom
"""
polynom = 0x04C11DB7


def reflect(value_input, bits):
    """
    Bit-wise reflection
    :param value_input: Value to reflect
    :param bits: Number of bits of data type
    :return: Reflected number
    """
    value = 0

    for i in range(bits):
        if (value_input & 1) != 0:
            value |= (1 << (bits - (i+1)))
        value_input >>= 1
    return value


def calc_from_byte(data_buf, crc_val=0xFFFFFFFF):
    """
    Calculate CRC32 from bytearray
    :param data_buf: Input data in bytearray format
    :param crc_val: Initial value of crc
    :return: Crc
    """
    crc_data = [0] * (len(data_buf) // 4)
    for i in range(len(data_buf) // 4):
        crc_data[i] = int.from_bytes(data_buf[i * 4:i * 4 + 4], byteorder='little', signed=False)
    return calculate(crc_data, crc_val=crc_val)


def calculate(data, crc_val=0xFFFFFFFF):
    """
    Calculate CRC32 from array of integers
    :param data: Input data as array of integers
    :param crc_val: Initial value of crc
    :return: Crc
    """
    table = [0] * 256

    for i in range(256):
        table[i] = reflect(i, 8) << 24
        for j in range(8):
            table[i] = ((table[i] << 1) ^ (polynom if (table[i] & (1 << 31)) != 0 else 0)) & 0xFFFFFFFF
        table[i] = reflect(table[i], 32)
    data_byte = b''

    for i in data:
        data_byte += reflect(i, 32).to_bytes(4, byteorder='little')
    for i in range(len(data_byte)):
        crc_val = (crc_val >> 8) ^ table[((crc_val & 0xff) ^ data_byte[i])] & 0xFFFFFFFF

    return reflect(crc_val, 32)
