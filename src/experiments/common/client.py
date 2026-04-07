from __future__ import annotations

from typing import Protocol, cast

from verifiers.types import ClientConfig, ClientType


class ClientSpecLike(Protocol):
    client_type: str
    api_key_var: str
    api_base_url: str


def build_client_config(spec: ClientSpecLike) -> ClientConfig:
    return ClientConfig(
        client_type=cast(ClientType, spec.client_type),
        api_key_var=spec.api_key_var,
        api_base_url=spec.api_base_url,
    )
