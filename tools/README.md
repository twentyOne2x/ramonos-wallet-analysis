# Reproduce the retained Ramonos investigation

Python 3.10 or newer and its standard library are sufficient. No Node packages,
wallet, signer or credentials are needed for offline replay. These case scripts
reproduce the disclosed wallet and fixed captures; they are not a generic wallet
indexer. The code reads schemas from `schemas/` next to `tools/`.

First extract the repository's raw evidence release **into the repository root**,
preserving `outputs/ramonos-launches-20261013/`. Then run:

```sh
python3 tools/replay.py --out /tmp/ramonos-replay
python3 tools/replay.py --out /tmp/ramonos-full-replay --full
```

The output must be a new empty directory outside the source tree. The runner
copies the retained evidence, recomputes in that copy, disables acquisition, and
compares the wallet receipt total, event/transaction counts, six other-quote
exclusions and failures against the frozen result. Input evidence is untouched.
Each script's output is captured in its scratch log; `replay-validation.json`
records completed stages. The exact total is 1,660,286,830,500 SOL/WSOL lamports.
This is a payout-receipt total, not net economic profit or all-launch attribution.

Individual scripts accept `RAMONOS_RESEARCH_ROOT` to choose an extracted data
workspace; the default is this repository. They write recomputed results into
that workspace, so use a copy when preserving evidence. Commands are:

```sh
python3 tools/census/capture.py
python3 tools/census/aggregate.py
python3 tools/census/launchlab.py
python3 tools/census/verify.py
python3 tools/own-fees/decode.py
python3 tools/own-fees/verify.py
python3 tools/own-fees/report.py
python3 tools/launchlab/analyze.py
python3 tools/launchlab/claims.py
python3 tools/launchlab/report.py
python3 tools/target-fees/replay.py
python3 tools/target-vaults/replay.py
python3 tools/target-vaults/amm_replay.py --latest
python3 tools/routes/snapshot.py outputs/ramonos-launches-20261013/census/launches.json
python3 tools/routes/finalize.py
```

`capture.py` reuses the retained fixed cutoff and pages; `aggregate.py` and
`launchlab.py` reconstruct the signed creation cohort. The default runner verifies
the census and reproduces creator-fee receipt decoding, transfer reconciliation
and report. `--full` also reproduces LaunchLab creator claims, direct GitHub
beneficiary history, native and WSOL upstream vault histories, and route snapshots.
Cached account reads retain their original slots and times; replay is not a fresh
state observation. The upstream vault replay separates rent/nonfee funding from
fee lots; the beneficiary replay separates account funding from mint payments.
The AMM full-lifetime attempt is incomplete in the retained evidence. The full
runner therefore uses `--latest`, the complete bounded window after the retained
native-unwrapping checkpoint, and does not label the earlier attempt complete.

Acquisition is opt-in: `RAMONOS_ALLOW_NETWORK=1` permits only the read-only methods
in `rpc_readonly.py`. Set `RAMONOS_RPC_URL` privately for a compatible indexed
provider. Public Solana RPC does not implement `getTransactionsForAddress` or
`getAsset`; those methods explicitly refuse public-RPC substitution. URLs and
credential fragments are omitted from errors/evidence. No network acquisition
was used to validate this portable adaptation. A fresh acquisition must use a
new workspace/configuration and retain separate observation times; it cannot
overwrite the historical cutoff and become historical proof.

`TOOLS-PROVENANCE.json` records original source hashes and adaptation descriptions.
The generic decoder removes unrelated investigation addresses and host paths.
`pump_pda.py` translates the official Pump SDK 4.0.0 seed formulas onto the retained
pure-Python Solana PDA implementation; offline checks compare derived addresses
with captured SDK outputs. Official MIT-licensed Pump SDK IDLs and a minimal factual Raydium LaunchLab
ABI subset (without documentation prose) are vendored under `schemas/`; the
Raydium subset carries its original source revision/hash and no relicensing claim.

## Trading and USD extension

Download and extract the `profit-audit-2026-10-13` evidence release into this clone. Run from the repository root:

```sh
python3 tools/replay_profit.py --out /tmp/ramonos-profit-replay
```

The output must be outside this repository and empty. This reproduces the trading inventory and actual cash ledgers, failed fees, standalone claim cash, and timestamped dollar valuations using frozen source responses. All price processors use `--offline`; the runner enables no signing, funding, claims or transactions. Creator receipts, original-wallet net cash and complete operator profit remain separate measures.
