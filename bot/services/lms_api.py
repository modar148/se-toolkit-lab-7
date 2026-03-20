"""
LMS API client — HTTP client for the backend API.

All endpoints require Bearer token authentication.
"""

import httpx
from config import config


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or config.lms_api_url).rstrip("/")
        self.api_key = api_key or config.lms_api_key
        self.timeout = 10.0  # seconds

    def _get_headers(self) -> dict:
        """Return headers with Bearer token."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_health(self) -> dict:
        """
        Check backend health by fetching items.
        
        Returns:
            dict with 'healthy' bool, 'item_count' int, 'error' str (if any)
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{self.base_url}/items/",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                items = response.json()
                return {
                    "healthy": True,
                    "item_count": len(items) if isinstance(items, list) else 0
                }
        except httpx.ConnectError as e:
            return {
                "healthy": False,
                "error": f"connection refused ({self.base_url}). Check that the services are running."
            }
        except httpx.HTTPStatusError as e:
            return {
                "healthy": False,
                "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
            }
        except httpx.TimeoutException:
            return {
                "healthy": False,
                "error": f"timeout connecting to {self.base_url} after {self.timeout}s"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }

    def get_labs(self) -> dict:
        """
        Get list of labs from backend.
        
        Returns:
            dict with 'labs' list, 'error' str (if any)
        """
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/items/",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                items = response.json()
                
                # Extract lab names from items
                labs = []
                for item in items:
                    if isinstance(item, dict):
                        # Try to get a meaningful name
                        name = item.get("name") or item.get("title") or item.get("id") or str(item)
                        labs.append({"id": item.get("id", ""), "name": name})
                    else:
                        labs.append({"id": str(item), "name": str(item)})
                
                return {"labs": labs}
        except httpx.ConnectError:
            return {
                "error": f"connection refused ({self.base_url})"
            }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_scores(self, lab_name: str) -> dict:
        """
        Get scores for a specific lab.

        Args:
            lab_name: The lab identifier (e.g., 'lab-04')

        Returns:
            dict with 'scores' list, 'error' str (if any)
        """
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/analytics/pass-rates/",
                    params={"lab": lab_name},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return {"scores": data}
        except httpx.ConnectError:
            return {
                "error": f"connection refused ({self.base_url})"
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"lab '{lab_name}' not found"}
            return {
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_pass_rates(self, lab_name: str) -> dict:
        """
        Get pass rates for a specific lab.

        Args:
            lab_name: The lab identifier (e.g., 'lab-04')

        Returns:
            dict with 'pass_rates' list, 'error' str (if any)
        """
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/analytics/pass-rates/",
                    params={"lab": lab_name},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()
                return {"pass_rates": data}
        except httpx.ConnectError:
            return {
                "error": f"connection refused ({self.base_url})"
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"lab '{lab_name}' not found"}
            return {
                "error": f"HTTP {e.response.status_code}"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_items(self) -> dict:
        """Get all items (labs and tasks)."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/items/",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"items": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_learners(self) -> dict:
        """Get all enrolled learners."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/learners/",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"learners": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_timeline(self, lab_name: str) -> dict:
        """Get submission timeline for a lab."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/analytics/timeline/",
                    params={"lab": lab_name},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"timeline": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_groups(self, lab_name: str) -> dict:
        """Get per-group performance for a lab."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/analytics/groups/",
                    params={"lab": lab_name},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"groups": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_top_learners(self, lab_name: str, limit: int = 5) -> dict:
        """Get top learners for a lab."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/analytics/top-learners/",
                    params={"lab": lab_name, "limit": limit},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"top_learners": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_completion_rate(self, lab_name: str) -> dict:
        """Get completion rate for a lab."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/analytics/completion-rate/",
                    params={"lab": lab_name},
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"completion_rate": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def trigger_sync(self) -> dict:
        """Trigger ETL sync."""
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(
                    f"{self.base_url}/pipeline/sync",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return {"sync": "triggered"}
        except Exception as e:
            return {"error": str(e)}


# Global client instance
lms_client = LMSAPIClient()
