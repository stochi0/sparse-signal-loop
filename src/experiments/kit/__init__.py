"""Shared experiment infrastructure (reporting, artifacts, factorial runner).

- Add a new **environment** under ``experiments/phase0/<name>/`` or ``experiments/phase1/<name>/``.
- Register output path key (e.g. ``phase0/lbp``) + report title in :mod:`experiments.kit.registry`.
- Extend derived stats in :mod:`experiments.kit.reporting` when you add metrics.
"""
