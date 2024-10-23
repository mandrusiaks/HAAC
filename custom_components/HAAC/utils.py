import hmac
import pytz
from datetime import datetime, date, time
from urllib.parse import quote


def add_hmac_signature(params):
    hasher = hmac.new("aps2020".encode(), digestmod="SHA1")
    output = {}
    for k, v in sorted(params.items()):
        quoted_v = quote(v)
        hasher.update(f"{k}{quoted_v}".encode())
        output[k] = v

    hash = hasher.hexdigest()
    output["checkcode"] = hash.upper()
    return output


def get_todays_midnight():
    today = date.today()
    return datetime.combine(today, datetime.min.time())
