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


class IRProvider:
    name = "IR"

    def discover(self, legal_name: str, task_type: str) -> List[DiscoveredSource]:
        now = datetime.now(timezone.utc)

        # Mock seeded IR link pattern for Week 2 skeleton
        domain_hint = legal_name.lower().replace(" ", "")
        return [
            DiscoveredSource(
                source_type="COMPANY_IR",
                title=f"{legal_name} - Investor Relations",
                url=f"https://www.{domain_hint}.com/investors",
                publisher=legal_name,
                published_at=now,
                metadata={"provider": "IR", "task_type": task_type},
            )
        ]