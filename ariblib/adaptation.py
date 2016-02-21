from datetime import timedelta


def adaptation_field_length(p):
    """パケットの adaptation_field_length を返す"""

    return p[0]


def discontinuity_indicator(p):
    """パケットの discontinuity_indicator を返す"""

    return (p[1] & 0x80) >> 7


def random_access_indicator(p):
    """パケットの random_access_indicator を返す"""

    return (p[1] & 0x40) >> 6


def elementary_stream_priority_indicator(p):
    """パケットの elementary_stream_priority_indicator を返す"""

    return (p[1] & 0x20) >> 5


def pcr_flag(p):
    """パケットの PCR_flag を返す"""

    return (p[1] & 0x10) >> 4


def opcr_flag(p):
    """パケットの OPCR_flag を返す"""

    return (p[1] & 0x08) >> 3


def splicing_point_flag(p):
    """パケットの splicing_point_flag を返す"""

    return (p[1] & 0x04) >> 2


def transport_private_data_flag(p):
    """パケットの transport_private_data_flag を返す"""

    return (p[1] & 0x02) >> 1


def adaptation_field_extension_flag(p):
    """パケットの adaptation_field_extension_flag を返す"""

    return p[1] & 0x01


def pcr(p):
    """パケットの pcr を返す"""

    if pcr_flag(p):
        base = ((p[2] << 25) | (p[3] << 17) | (p[4] << 9) | (p[5] << 1) |
                ((p[6] & 0x80) >> 7))
        extension = ((p[6] & 0x01) << 8) | p[7]
        pcr = base * 300 + extension
        pcr_hz = 27000000
        second = pcr / pcr_hz
        return timedelta(seconds=second)
