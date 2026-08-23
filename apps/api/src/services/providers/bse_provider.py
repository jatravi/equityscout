from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class DiscoveredSource:
    source_type: str
    title: str
    url: str
    publisher: str
    published_at: Optional[datetime]
    metadata: dict


class BSEProvider:
    name = "BSE"

    def discover(self, legal_name: str, bse_code: Optional[str], task_type: str) -> List[DiscoveredSource]:
        code = bse_code or "000000"
        now = datetime.now(timezone.utc)

        # Mock skeleton output (replace with real BSE integration next)
        return [
            DiscoveredSource(
                source_type="BSE_FILING",
                title=f"{legal_name} - Corporate Filings",
                url=f"https://www.bseindia.com/stock-share-price/{legal_name.replace(' ', '-')}/{code}/",
                publisher="BSE",
                published_at=now,
                metadata={"provider": "BSE", "task_type": task_type, "bse_code": code},
            )
        ]