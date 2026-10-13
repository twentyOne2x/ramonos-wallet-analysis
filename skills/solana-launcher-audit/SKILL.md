---
name: solana-launcher-audit
description: Audit public Solana launcher wallets and signed token creations, trace Pump or Raydium creator-fee destinations, and reconcile actual recipient receipts and pending fees. Use for launch censuses or claimed/unclaimed fee analysis, not purchases, signing, or wallet recovery.
---

# Solana launcher audit

Produce a source-bound wallet launch census and fee accounting that distinguishes
configured recipients, actual payments, pending custody and human attribution.
Keep the requested wallet/cohort and cutoff. Public read-only analysis authorizes
no purchases, claims, transfers, or configuration changes.

## Start from the existing evidence

Find the existing analysis root, raw captures, launch register and computation
scripts before fetching again. Use mint addresses as identities. Establish whether
a supplied address is a wallet, mint or program account; a token CA is not its
creator wallet. Attribute a wallet to a human only from a retained primary public
statement or equivalent evidence. Multiple-wallet statements do not identify the
other wallets. A nonseed recipient has unknown ownership, not proven bot status.

Use official Solana, Pump and Raydium SDK/IDL schemas for changed chain boundaries.
Pin the source revision or package version. Verify program owner, PDA seeds,
authority, mint, quote mint and decimals against the raw account. Preserve absent
legacy fields as null; decode failure is not false or zero.

## Census and coverage

- Enumerate finalized successful wallet transactions to a fixed cutoff. Retain
  pagination requests, cursors, terminal response, duplicates and gaps. A provider
  cap or partial page chain is not complete history.
- Admit a launch only when the wallet signed the actual creation and the exact
  mint's initialization is matched in that transaction. Buys, fee-creator status,
  metadata mentions and unsigned third-party creations do not establish launches.
- Bind each admitted row to signature, slot, timestamp, program, mint and creation
  witness. Group launch frequency by explicit UTC day/week; distinguish active days
  from all calendar days and state the date range.
- Keep census, route, receipt and pending snapshots' cutoffs separate. Use a final
  same-slot read of affected custody/counters when feasible, without describing
  earlier histories as one atomic snapshot.

## Route and fee analysis

Read [the accounting contract](references/accounting.md) before computing amounts.

Decode each current route, including ordinary creator, wallet sharing, social,
intermediary, donation, holder rewards and LaunchLab. Keep current configuration
separate from historical distribution. Replay actual old recipients at each
payout; today's split cannot rewrite past payments. Native holder mode is distinct
from social developer claims. A holder flag proves mode, not delivery performance.

Deduplicate pooled creator/quote vaults across mints. Report asset-specific gross
receipts, source-attributed fees, net native wallet cash and pending fees as
separate measures. Use destination ownership and actual transfer receipts for
claimed status. UsePaid or another intermediary's collection leaves downstream
human settlement unknown without independent evidence.

For current pending custody, a verified exact zero checkpoint plus uninterrupted
replay to the final snapshot can suffice even when older history is partial.
Preserve that older gap; do not turn the checkpoint proof into lifetime coverage.
For social custody, replay the whole account's fee lots and claim movements so
multiple mints and withdrawals cannot be assigned to a convenient single mint.

## Portable tools and outputs

Use the [public tools](https://github.com/twentyOne2x/ramonos-wallet-analysis/tree/main/tools)
documentation to select acquisition and computation commands. The retained commands
reproduce the Ramonos wallet/cutoff; they are not a generic wallet acquisition API.
For a different wallet, adapt the relevant scope/configuration in the analysis
workspace, preserve the original captures, and rerun the signed-creation and
accounting checks. Do not claim a changed wallet flag exists when it does not.
The tools are evidence processors; completeness and attribution still require
the checks above. An installed skill can locate the analysis clone from
its remote or existing working directory; do not copy private workspace paths.

From the repository root, Python 3 commands for retained evidence include:

```sh
python3 tools/census/verify.py
python3 tools/target-fees/replay.py
python3 tools/target-vaults/amm_replay.py --latest
```

These write derived evidence, so use an isolated replay workspace described in the
tool documentation. `RAMONOS_RESEARCH_ROOT` selects data there; network is disabled
by default. Verify coverage and exit status, not merely file creation. Retained
commands require their named input files; missing inputs remain unproved.

Deliver a mint register, recipient ledger, coverage/unknowns and concise report,
with relative links to retained public data rather than embedded case data.
For each percentage, state its numerator, denominator, unit and scope. Destination
categories must be mutually exclusive and sum to the stated census. Per-wallet
or per-asset samples do not justify annual forecasts without explicit qualifying
launch frequency, revenue-distribution and cost assumptions.

If publication is in the user request, finish its authorized public artifact using
public provenance, portable paths and credential-free sources. Preserve raw
amounts/signatures/hashes; exclude provider secrets and unrelated private material.
Do not introduce another approval layer for already-authorized publication.

The retained [Ramonos example](https://github.com/twentyOne2x/ramonos-wallet-analysis/tree/main/outputs/ramonos-launches-20261013)
uses disclosed wallet `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`, direct
GitHub mint `4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump` and intermediary
mint `EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM`. These are examples,
not the default scope for other wallets; read their data rather than hard-coding
case conclusions into a new analysis.

Example request: “Use $solana-launcher-audit on this disclosed launcher wallet,
census its signed launches through a fixed cutoff, and show who actually received
creator fees, what remains pending, and which amounts are unknown.”
