## Sparse Signal Loop

### Run experiments (Prime pod)

#### 1) Local (your laptop)

Upload your SSH public key (one-time per machine/account) so new pods accept `prime pods ssh`:

```bash
./scripts/prime_ssh_key_upload.sh ~/.ssh/id_ed25519.pub
prime config set-ssh-key-path ~/.ssh/id_ed25519
```

Create a pod:

```bash
# optional: export PRIME_POD_SKU=6ac679
./scripts/prime_pod.sh create
prime pods list
prime pods ssh <pod-id>
```

#### 2) On the pod

Bootstrap deps + clone + install Python deps:

```bash
export SPARSE_SIGNAL_LOOP_REPO="https://github.com/<YOU>/sparse-signal-loop.git"
./scripts/prime_pod.sh bootstrap
cd ~/sparse-signal-loop
```

Create `.env` (required for real runs):

```bash
printf "PRIME_API_KEY=%s\n" "<your_prime_api_key>" > .env
# optional:
# printf "WANDB_API_KEY=%s\n" "<your_wandb_api_key>" >> .env
```

Run an end-to-end smoke (phase0/phase1/phase2 in parallel, logs under `outputs/smoke_logs/`):

```bash
./scripts/smoke.sh
```

Or run a single phase:

```bash
./scripts/phase0/lbp.sh -n 4 -r 1
./scripts/phase1/lbp.sh --smoke
./scripts/phase2/lbp.sh --smoke
```

#### 3) Cleanup (back on your laptop)

```bash
prime pods terminate <pod-id>
```

