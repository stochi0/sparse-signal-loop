from __future__ import annotations

from pathlib import Path
from typing import Any

from verifiers.types import ClientConfig, EvalConfig

from experiments.common.client import build_client_config as build_shared_client_config
from experiments.phase1.schema import Phase1Cell

from .env_args import build_env_args, env_id_for_cell
from .schema import Phase1MiniSweSpec


def build_client_config(spec: Phase1MiniSweSpec) -> ClientConfig:
    return build_shared_client_config(spec)


def build_eval_config(
    spec: Phase1MiniSweSpec,
    cell: Phase1Cell,
    *,
    cell_output_dir: Path,
) -> EvalConfig:
    sampling: dict[str, Any] = dict(spec.sampling_args)
    return EvalConfig(
        env_id=env_id_for_cell(cell),
        env_args=build_env_args(cell, spec),
        env_dir_path=spec.env_dir_path,
        output_dir=str(cell_output_dir.resolve()),
        model=spec.model,
        client_config=build_client_config(spec),
        sampling_args=sampling,
        num_examples=spec.num_examples,
        rollouts_per_example=spec.rollouts_per_example,
        max_concurrent=spec.max_concurrent,
        num_workers=spec.num_workers,
        max_retries=spec.max_retries,
        verbose=spec.verbose,
        debug=spec.debug,
        save_results=spec.save_results,
        state_columns=None,
        extra_env_kwargs={},
        disable_env_server=False,
        independent_scoring=False,
    )
