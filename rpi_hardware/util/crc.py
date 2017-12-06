def _add_to_crc8(b, crc):
    if b < 0:
        b += 256
    for i in range(8):
        odd = ((b ^ crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if odd:
            crc ^= 0x8C
    return crc


def crc8_value(byte_list):
    """
    Gives CRC8 value for sequence of bytes.

    :param byte_list: list of byte values
    :return: CRC8 single byte value as integer
    """
    check = 0
    for cur_byte in byte_list:
        check = _add_to_crc8(cur_byte, check)
    return check


def crc8_check(byte_list, crc_value):
    """
    Performs crc8 check
    :param byte_list:
    :param crc_value:
    :return:
    """
    return crc8_value(byte_list) == crc_value


if __name__ == '__main__':
    for i in range(256):
        print("([{}], {}),".format(i, crc8_value([i])))
