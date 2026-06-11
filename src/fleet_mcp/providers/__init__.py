"""Telematics data providers.

The `TelematicsProvider` protocol is the seam that, in a production system,
would talk to a real GraphQL/REST telematics backend with IAM/OAuth2 auth.
Here we ship a `MockTelematicsProvider` so the server runs with zero
infrastructure and zero secrets.
"""

from fleet_mcp.providers.base import TelematicsProvider
from fleet_mcp.providers.mock import MockTelematicsProvider

__all__ = ["TelematicsProvider", "MockTelematicsProvider"]
