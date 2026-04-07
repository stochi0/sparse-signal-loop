# Temporary workaround until prime-sandboxes supports env overwrite reliably.
PATH = "PATH=/opt/miniconda3/bin:/testbed/.venv/bin:/root/.local/bin:/root/.cargo/bin:/go/bin:/usr/local/go/bin:/usr/local/cargo:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ENV_VARS = f"export {PATH} PAGER=cat MANPAGER=cat LESS=-R PIP_PROGRESS_BAR=off TQDM_DISABLE=1;"
