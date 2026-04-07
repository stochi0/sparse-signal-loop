# Temporary workaround until prime-sandboxes supports env overwrite reliably.
PATH_SWEBENCH = (
    "PATH=/opt/miniconda3/envs/testbed/bin:/opt/miniconda3/bin:/usr/local/sbin:"
    "/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
)
PATH_R2E = "PATH=/testbed/.venv/bin:/root/.local/bin:/root/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV_VARS_SWEBENCH = f"export {PATH_SWEBENCH} PAGER=cat MANPAGER=cat LESS=-R PIP_PROGRESS_BAR=off TQDM_DISABLE=1;"
ENV_VARS_R2E = f"export {PATH_R2E} PAGER=cat MANPAGER=cat LESS=-R PIP_PROGRESS_BAR=off TQDM_DISABLE=1;"
