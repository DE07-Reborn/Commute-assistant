import os
import requests
import pandas as pd
import json
import re
import logging
log = logging.getLogger(__name__)
class aladin_api_utils:
    BASE_URL = "https://www.aladin.co.kr/ttb/api/ItemList.aspx"
    VERSION = "20131101"    # API 최신버전: 20131101
    def __init__(self):
        self.ttbkey = os.getenv("ALADIN_KEY")
        if not self.ttbkey:
            raise ValueError("ALADIN_KEY not set")
        self.timeout = 10
    def fetch_bestseller(self, start:int, max_results:int):
        params = {
            "ttbkey": self.ttbkey,
            "QueryType": "Bestseller",
            "SearchTarget": "Book",
            "start": start,
            "MaxResults": max_results,
            "output": "JS",
            "Version": self.VERSION,
            "OptResult": "ebookList"
        }
        res = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
        res.raise_for_status()
        try:
            data = json.loads(res.text, strict=False)
        except json.JSONDecodeError as e:
            log.warning(
                f"JSON decode failed (start={start}). Cleaning control chars. "
                f"response_snippet={res.text[:500]}"
            )
            # 2차: 제어문자 제거 후 재시도
            clean_text = re.sub(r"[\x00-\x1F\x7F]", "", res.text)
            data = json.loads(clean_text)
        items = data.get("item", [])
        if not items:
            log.warning(f"No items returned (start={start})")
        df = pd.DataFrame(items)
        return df