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


# Global client instance
lms_client = LMSAPIClient()
