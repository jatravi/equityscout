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


class NSEProvider:
    name = "NSE"

    def discover(self, legal_name: str, nse_symbol: Optional[str], task_type: str) -> List[DiscoveredSource]:
        symbol = nse_symbol or legal_name.replace(" ", "-").upper()[:10]
        now = datetime.now(timezone.utc)

        # Mock skeleton output (replace with real NSE integration next)
        return [
            DiscoveredSource(
                source_type="NSE_ANNOUNCEMENT",
                title=f"{legal_name} - Latest Corporate Announcement",
                url=f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}",
                publisher="NSE",
                published_at=now,
                metadata={"provider": "NSE", "task_type": task_type, "symbol": symbol},
            ),
            DiscoveredSource(
                source_type="NSE_RESULTS",
                title=f"{legal_name} - Financial Results",
                url=f"https://www.nseindia.com/companies-listing/corporate-filings-financial-results?symbol={symbol}",
                publisher="NSE",
                published_at=now,
                metadata={"provider": "NSE", "task_type": task_type, "symbol": symbol},
            ),
        ]