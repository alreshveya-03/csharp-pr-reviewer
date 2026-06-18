"""Verification script for Review Summary Generator and Publish Manager."""
import asyncio
import logging
import sys
import io
from typing import Any

# Reconfigure stdout to support unicode emojis on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.core.config import AppConfig
from src.core.logging import configure_logging
from src.models.pull_request import PullRequest
from src.models.findings import Finding
from src.models.review import Review
from src.interfaces.github_client import IGitHubClient
from src.services.publishing.review_formatter import ReviewFormatter
from src.services.publishing.review_summary_generator import ReviewSummaryGenerator
from src.services.publishing.publish_manager import PublishManager

configure_logging("INFO")
logger = logging.getLogger("VerifyPublishing")

class MockGitHubClient(IGitHubClient):
    """Mock implementation of IGitHubClient for testing and offline verification."""
    async def get_pull_request(self, pr_number: int) -> PullRequest:
        return PullRequest(
            pr_number=pr_number,
            title="Mock Pull Request",
            description="Mock Description",
            state="open",
            is_draft=False,
            head_sha="mock-head-sha",
            base_sha="mock-base-sha",
            html_url="https://github.com/mock/repo/pull/1"
        )

    async def get_changed_files(self, pr_number: int) -> list[dict[str, Any]]:
        return []

    async def get_raw_diff(self, pr_number: int) -> str:
        return ""

    async def submit_review(self, pr_number: int, review: Review) -> None:
        pass

    async def get_review_comments(self, pr_number: int) -> list[dict[str, Any]]:
        return []

def run_verification() -> None:
    logger.info("Initializing configuration parameters.")
    config = AppConfig()
    
    # 1. Instantiate services
    formatter = ReviewFormatter()
    generator = ReviewSummaryGenerator(formatter)
    github_client = MockGitHubClient()
    manager = PublishManager(github_client, formatter, generator, config)

    # 2. Build mock pull request and findings
    pr = PullRequest(
        pr_number=421,
        title="Refactor Data Sync Service to use Async Streams",
        description="Replaces batch streams with Async Enumerables.",
        state="open",
        is_draft=False,
        head_sha="a1b2c3d4e5f67890a1b2c3d4e5f67890abcdef12",
        base_sha="f6e5d4c3b2a10987f6e5d4c3b2a10987abcdef12",
        html_url="https://github.com/AcmeOrg/enterprise-backend/pull/421"
    )

    findings = [
        Finding(
            file_path="src/Core/Services/Sync.cs",
            line_number=11,
            rule_id="CS-PERF-01",
            category="Performance",
            severity="High",
            title="Avoid blocking async call",
            description="Ensure asynchronous calls do not block execution threads.",
            suggestion="var x = await FetchAsync();",
            confidence_score=0.95
        ),
        Finding(
            file_path="src/Core/Services/Sync.cs",
            line_number=15,
            rule_id="CS-SEC-01",
            category="Security",
            severity="Critical",
            title="SQL Injection vulnerability",
            description="Sanitize raw SQL queries.",
            suggestion="var data = await _ctx.Users.FromSqlRaw(\"SELECT * FROM Users WHERE Id = {0}\", id).ToListAsync();",
            confidence_score=0.98
        )
    ]

    stats = {
        "run_id": "test-run-id-12345",
        "pr_number": 421,
        "duration_s": 4.25,
        "files_analyzed": 2,
        "chunks_processed": 3,
        "total_tokens": 4250,
        "findings_count": 2,
        "critical_count": 1,
        "high_count": 1,
        "medium_count": 0,
        "low_count": 0,
        "info_count": 0,
        "errors_logged": 0
    }

    review = Review(
        pull_request=pr,
        findings=findings,
        verdict="REQUEST_CHANGES",
        summary_markdown="",
        stats=stats
    )

    logger.info("Executing dry-run review publication.")
    asyncio.run(manager.publish_review(421, review, dry_run=True))
    logger.info("Verification completed successfully.")

if __name__ == "__main__":
    run_verification()
