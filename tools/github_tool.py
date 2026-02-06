import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tools.base_tool import BaseTool
except ImportError:
    from .base_tool import BaseTool

from config import Config


class GitHubTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="github_search",
            description="Search GitHub repositories and fetch repository details"
        )
        self.base_url = Config.GITHUB_API_URL
        self.headers = {
            "Authorization": f"token {Config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def execute(self, **kwargs) -> dict:
        # Remove 'operation' parameter if it exists (it's for the planner, not this method)
        # The planner might include it, but we don't need it here
        kwargs.pop('operation', None)

        # Check if this is a search or get_repo request
        if 'query' in kwargs:
            return self.search_repositories(**kwargs)
        elif 'owner' in kwargs and 'repo' in kwargs:
            return self.get_repository(**kwargs)
        else:
            # Default to search with a generic query
            return self.search_repositories(query="python", **kwargs)

    def search_repositories(self, query: str, per_page: int = 5, **kwargs) -> dict:
        """Search GitHub repositories

        Args:
            query: Search query (required)
            per_page: Number of results (default: 5)
            **kwargs: Other parameters (ignored)
        """
        params = {
            "q": query,
            "per_page": per_page,
            "sort": "stars",
            "order": "desc"
        }

        try:
            response = self.make_request(
                method="GET",
                url=f"{self.base_url}/search/repositories",
                headers=self.headers,
                params=params
            )

            repos = []
            for item in response.get("items", [])[:per_page]:
                repos.append({
                    "name": item["full_name"],
                    "description": item["description"] or "No description",
                    "stars": item["stargazers_count"],
                    "url": item["html_url"],
                    "language": item["language"],
                    "topics": item.get("topics", [])
                })

            return {
                "query": query,
                "total_count": response.get("total_count", 0),
                "repositories": repos
            }
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "total_count": 0,
                "repositories": []
            }

    def get_repository(self, owner: str, repo: str, **kwargs) -> dict:
        """Get details of a specific repository

        Args:
            owner: Repository owner (required)
            repo: Repository name (required)
            **kwargs: Other parameters (ignored)
        """
        try:
            response = self.make_request(
                method="GET",
                url=f"{self.base_url}/repos/{owner}/{repo}",
                headers=self.headers
            )

            return {
                "name": response["full_name"],
                "description": response["description"] or "No description",
                "stars": response["stargazers_count"],
                "forks": response["forks_count"],
                "issues": response["open_issues_count"],
                "url": response["html_url"],
                "language": response["language"],
                "created_at": response["created_at"],
                "updated_at": response["updated_at"],
                "topics": response.get("topics", [])
            }
        except Exception as e:
            return {
                "error": str(e),
                "owner": owner,
                "repo": repo
            }