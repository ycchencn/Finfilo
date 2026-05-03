"""
 * @author Yc
 * Chaos isn't a pit. Chaos is a ladder. - Littlefinger
 * Copyright (c) 2025 yccheni@163.com. All rights reserved.
"""

from eodhd import APIClient

class EodHD(APIClient):

    def __init__(self, api_key: str) -> None:
        super().__init__(api_key)
