"""Krado API client."""

import logging
from typing import Any, cast

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from .const import GRAPHQL_ENDPOINT, GRAPHQL_SCHEMA

_LOGGER = logging.getLogger(__name__)


class Krado:
    """Krado API client class."""

    _token: str | None = None

    def __init__(self, token: str | None = None) -> None:
        """Initialize the client."""
        self._token = token
        transport = AIOHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            headers={"Authorization": f"Bearer {self._token}"} if token else {},
        )
        self._client = Client(schema=GRAPHQL_SCHEMA, transport=transport)

    @property
    def token(self) -> str | None:
        """Return the token, if any."""
        return self._token

    async def close(self) -> None:
        """Close the client transport."""
        await self._client.close_async()

    async def login(self, email: str, password: str) -> None:
        """Login."""
        query = gql(
            """
            mutation SignIn($email: String!, $password: String!) {
                login(email: $email, password: $password) {
                    token
                }
            }
        """
        )
        params = {"email": email, "password": password}
        result = await self._client.execute_async(query, variable_values=params)
        if errors := result.get("errors"):
            # oops
            pass
        self._token = result["login"]["token"]
        cast(AIOHTTPTransport, self._client.transport).headers = {
            "Authorization": f"Bearer {self._token}"
        }

    async def query_plants(self) -> list[dict[str, Any]]:
        """Query plants."""
        query = gql(
            """
            query Plants {
                plants {
                    ...PlantFragment
                    sensor {
                        __typename
                        id
                        isConnected
                        isActive
                        firmwareVersion
                        serialNumber
                        humidityRange
                        humidityStatus
                        lightRange
                        lightStatus
                        moistureRange
                        moistureStatus
                        temperatureRange
                        temperatureStatus
                        lastReading {
                            id
                            createdAt
                            battery
                            humidity
                            light
                            moisture
                            signal
                            temperature
                        }
                    }
                    plantActions {
                        id
                        kind
                        severity
                        __typename
                    }
                    __typename
                }
            }
            fragment PlantFragment on Plant {
                id
                name
                kind
                lastAnalyzedAt
                humidityStatus
                lightStatus
                moistureStatus
                temperatureStatus
                status
                plantClassification {
                    id
                    name
                    family
                    genus
                    illustrationUrl
                    isHanging
                    hasMoreInfo
                    preferredName
                    __typename
                }
                __typename
            }
        """
        )
        result = await self._client.execute_async(query)
        return result.get("plants")
