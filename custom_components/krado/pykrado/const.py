"""Constants."""

from __future__ import annotations

import os
from typing import Final

GRAPHQL_ENDPOINT: Final = "https://prod.api.krado.co/graphql"

__GRAPHQL_SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.graphql")
with open(__GRAPHQL_SCHEMA_FILE, "r", encoding="utf8") as file:
    GRAPHQL_SCHEMA: Final = file.read()
