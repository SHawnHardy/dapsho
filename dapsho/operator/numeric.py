"""
@Author     : Hengyu Shang
@License    : MIT License
"""

import logging

logger = logging.getLogger(__name__)


def convert_percent_str_to_float(percent_str):
    if percent_str[-1] != "%":
        return float(percent_str)
    return float(percent_str[:-1]) / 100
