import base64
from datetime import datetime
from dateutil import tz


def convert_timestamp_to_ksa_string(timestamp_string):
    naive_datetime = datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S.%f")
    ksa_timezone = tz.gettz('Asia/Riyadh')
    localized_datetime = naive_datetime.replace(tzinfo=ksa_timezone)
    ksa_string = localized_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    return ksa_string


def encode_tlv(tag, value):
    tag_byte = bytes([tag])
    length_byte = bytes([len(value)])
    value_byte = value.encode('utf-8')
    tlv_encoded = tag_byte + length_byte + value_byte
    return tlv_encoded


def generate_qrcode(company_name, company_id, timestamp, amount, tax):
    tlv_strings = [
        encode_tlv(1, company_name),
        encode_tlv(2, company_id),
        encode_tlv(3, convert_timestamp_to_ksa_string(timestamp)),
        encode_tlv(4, amount),
        encode_tlv(5, tax)
    ]

    # print(tt)
    tlv_base_string = b''.join(tlv_strings)
    base64_encoded = base64.b64encode(tlv_base_string)

    return base64_encoded.decode()
