"""Verification script for ReviewAgent orchestrator and validation pipeline."""
import asyncio
import logging
from typing import Any
from src.core.config import AppConfig
from src.core.container import Container
from src.core.logging import configure_logging

# Client interfaces & models
from src.interfaces.github_client import IGitHubClient
from src.interfaces.llm_client import ILLMClient
from src.interfaces.reviewer import IReviewer
from src.models.pull_request import PullRequest
from src.models.review import Review

# Services
from src.services.diff.csharp_filter import CSharpFileFilter
from src.services.diff.diff_parser import DiffParser
from src.services.diff.diff_extractor import DiffExtractor
from src.services.diff.line_mapper import LineMapper
from src.services.prompts.prompt_builder import PromptBuilder
from src.services.prompts.review_prompt_manager import ReviewPromptManager
from src.services.review.review_validator import ReviewValidator
from src.services.review.severity_engine import SeverityEngine
from src.services.review.finding_filter import FindingFilter

# Orchestrator
from src.agent.review_agent import ReviewAgent
from src.services.publishing.review_formatter import ReviewFormatter
from src.services.publishing.review_summary_generator import ReviewSummaryGenerator
from src.services.publishing.publish_manager import PublishManager

configure_logging("INFO")
logger = logging.getLogger("VerifyAgent")

class MockGitHubClient(IGitHubClient):
    """Mock implementation of IGitHubClient for testing and offline verification."""
    async def get_pull_request(self, pr_number: int) -> PullRequest:
        return PullRequest(
            pr_number=pr_number,
            title="Mock Pull Request",
            description="Mock Description",
            state="open",
            is_draft=False,
            head_sha="a1b2c3d4e5f67890a1b2c3d4e5f67890abcdef12",
            base_sha="f6e5d4c3b2a10987f6e5d4c3b2a10987abcdef12",
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


class MockLLMClient(ILLMClient):
    """Mock implementation of ILLMClient for testing and offline verification."""
    async def generate_structured_content(
        self, 
        prompt: str, 
        system_instruction: str | None = None,
        response_schema: dict[str, Any] | None = None
    ) -> str:
        return '{"findings": []}'


class VerifyMockGitHubClient(MockGitHubClient):
    async def get_changed_files(self, pr_number: int) -> list[dict[str, Any]]:
        return [
            {
                "filename": "src/Core/Services/Sync.cs",
                "status": "modified",
                "additions": 14,
                "deletions": 2,
                "changes": 16,
                "patch": (
                    "@@ -10,3 +10,4 @@ public class Sync {\n"
                    "+    public async Task RunAsync() {\n"
                    "+        var x = await FetchAsync();\n"
                    "     }\n"
                )
            }
        ]

class VerifyMockLLMClient(MockLLMClient):
    async def generate_structured_content(
        self, 
        prompt: str, 
        system_instruction: str | None = None,
        response_schema: dict[str, Any] | None = None
    ) -> str:
        return (
            "{\n"
            "  \"findings\": [\n"
            "    {\n"
            "      \"file_path\": \"src/Core/Services/Sync.cs\",\n"
            "      \"line_number\": 11,\n"
            "      \"rule_id\": \"CS-PERF-01\",\n"
            "      \"category\": \"Performance\",\n"
            "      \"severity\": \"High\",\n"
            "      \"title\": \"Avoid blocking async call\",\n"
            "      \"description\": \"Ensure asynchronous calls do not block execution threads.\",\n"
            "      \"suggestion\": \"var x = await FetchAsync();\",\n"
            "      \"confidence_score\": 0.95\n"
            "    }\n"
            "  ]\n"
            "}"
        )

async def run_verification() -> None:
    logger.info("Setting up Container registrations.")
    container = Container()
    container.reset()
    
    # 1. Register configurations
    config = AppConfig(
        GITHUB_TOKEN="mock_token_123",
        GITHUB_REPOSITORY="AcmeOrg/enterprise-backend",
        GITHUB_PR_NUMBER=421,
        GEMINI_API_KEY="mock_key_123"
    )
    container.register_singleton(AppConfig, config)
    
    # 2. Register mock clients
    container.register_singleton(IGitHubClient, VerifyMockGitHubClient())
    container.register_singleton(ILLMClient, VerifyMockLLMClient())
    
    # 3. Register processing services
    container.register_singleton(CSharpFileFilter, CSharpFileFilter(config))
    parser = DiffParser()
    container.register_singleton(DiffParser, parser)
    container.register_singleton(DiffExtractor, DiffExtractor(parser))
    container.register_singleton(LineMapper, LineMapper())
    
    # 4. Register prompt services
    container.register_singleton(PromptBuilder, PromptBuilder())
    container.register_singleton(ReviewPromptManager, ReviewPromptManager())
    
    # 5. Register review services
    container.register_singleton(ReviewValidator, ReviewValidator())
    container.register_singleton(SeverityEngine, SeverityEngine(config))
    container.register_singleton(FindingFilter, FindingFilter())
    
    # Register publishing services
    formatter = ReviewFormatter()
    summary_generator = ReviewSummaryGenerator(formatter)
    container.register_singleton(ReviewFormatter, formatter)
    container.register_singleton(ReviewSummaryGenerator, summary_generator)
    
    container.register_factory(
        PublishManager,
        lambda: PublishManager(
            github_client=container.resolve(IGitHubClient),
            formatter=container.resolve(ReviewFormatter),
            summary_generator=container.resolve(ReviewSummaryGenerator),
            config=config
        )
    )

    # 6. Register concrete ReviewAgent orchestrator
    container.register_factory(
        IReviewer,
        lambda: ReviewAgent(
            publish_manager=container.resolve(PublishManager),
            github_client=container.resolve(IGitHubClient),
            llm_client=container.resolve(ILLMClient),
            file_filter=container.resolve(CSharpFileFilter),
            diff_extractor=container.resolve(DiffExtractor),
            line_mapper=container.resolve(LineMapper),
            prompt_builder=container.resolve(PromptBuilder),
            prompt_manager=container.resolve(ReviewPromptManager),
            validator=container.resolve(ReviewValidator),
            severity_engine=container.resolve(SeverityEngine),
            finding_filter=container.resolve(FindingFilter)
        )
    )

    logger.info("Resolving and executing ReviewAgent.")
    reviewer = container.resolve(IReviewer)
    review_output = await reviewer.review_pull_request(421)
    
    logger.info("Verification completed successfully:")
    logger.info(f" - Verdict: {review_output.verdict}")
    logger.info(f" - Findings generated: {len(review_output.findings)}")
    logger.info(f" - Stats duration: {review_output.stats.get('duration_s')}s")
    logger.info(f" - Run ID: {review_output.stats.get('run_id')}")
    logger.info(f" - Summary:\n{review_output.summary_markdown}")

if __name__ == "__main__":
    asyncio.run(run_verification())
