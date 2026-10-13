# Creator-fee accounting contract

Read this when deriving receipt, fee-revenue, pending or claim totals. Keep raw
integer quantities and asset identities through computation; format decimals last.

## Evidence bindings

Each payout row needs signature, slot, timestamp, outer/inner instruction position,
program, source account, destination, destination owner, quote mint, raw amount,
decimals and the raw source payload SHA-256. Bind CPI/event decoding to that payload.
One transaction can contain several distributions; signature-only deduplication
loses receipts. Use instruction/event identities and reconcile source debits with
individual destination credits. Retain unexplained residuals explicitly.

For Pump AMM CollectCoinCreatorFee, resolve the actual wallet-owned destination ATA,
its mint and owner, and the source debit. A sweep into native custody or an unwrap
is internal movement of the same fee, not another earned receipt. For Raydium,
resolve the specific launch program/platform configuration and creator/quote vault
from official schemas; a canonical creator withdrawal proves that asset's receipt,
not an arbitrary individual mint's lifetime revenue.

## Assets and measures

- Raw token quantities with different mints/decimals never sum. Report SOL, USD1,
  USDC or other quote assets separately unless a stated conversion is requested.
- SOL and canonical WSOL both have nine decimals and can represent one economic
  SOL subtotal. Label custody components and eliminate wraps, unwraps and internal
  sweeps so the same fee is counted once. Do not infer WSOL from ticker text.
- Gross fee-payout receipts are actual amounts received through a canonical payout.
  They may include proven released funding/rent; isolate that before calling the
  result pure fee-origin revenue. A received payout is not net profit.
- Net native wallet cash reconciles all pre/post balances once per transaction:
  fees, rent deposits, rent refunds, unrelated transfers and fee receipts. Do not
  subtract transaction fees repeatedly for multiple payout events. Keep token cash
  separate from native cash and disclose other activity; profit requires costs.
- Pooled direct claims can be attributed to the creator/quote account and actual
  recipient, but not strictly to a mint cohort without separate provenance.

## Pending and funding conservation

Use integer conservation: opening custody + fee inflows + nonfee inflows − payout
and other outflows = closing custody. Split fee-origin and nonfee lots. Original
account funding, rent reserves, reduced-rent releases and unrelated deposits do
not become fee revenue because the balance exceeds today's rent minimum. Unknown
native AMM residual provenance remains excluded from verified pending fees.

A current ATA pending proof may start from an authoritative exact zero balance.
Show the checkpoint's transaction/state, uninterrupted later finalized history and
closing account equality. This closes present custody without asserting older
lifetime completeness. Native account checkpoints must separately retain rent and
funding lots; spendable balance is not automatically fee-origin balance. Unswept
curve/pool fee counters stay separate from custody balances until reconciliation.

Social account accounting uses the whole account: preserve each mint-tagged fee
lot, initial funding, distribution and claim, and reconcile total custody/counters.
A zero authoritative claim counter and complete relevant replay can establish no
claim at the stated snapshot. Nonzero aggregate claims do not identify a particular
mint's claim without allocation evidence. Upstream mint-tagged pending plus social
custody is additive only when replay proves they are distinct unsent and sent lots.

## Recipient meaning

“Claimed by developer” means the actual target developer wallet received funds.
A current social identity, expected GitHub account or metadata name does not prove
that wallet's ownership or receipt. Collection by an intermediary proves collection
there; downstream settlement remains unknown. Wallet sharing recipients may be
paid automatically by distribution and need no social authentication claim.

Use the historically effective recipient list for each payout, including fees
flushed to old recipients before a sharing configuration update. Distinguish
current route counts, historical receipts, verified fee-origin income and current
allocation of pending funds. Apply basis-point rounding in integer units, state
unallocated dust, and avoid summing repeated pooled-vault rows across tokens.

## Trading profit and historical USD

A quote-asset margin uses actual buy debits and sale credits including venue fees. For AMM exact-quote buys, reserve principal and total quote debit can be different fields; bind the quote amount to the actual transfer under the same parent instruction. A fee-only ABI may omit trade instructions/events, so close every decoder dependency before labeling missing trades as transfers.

Track raw inventory, transfers, burns and unsold balances per mint. Fully matched positions, transferred positions, remaining inventory and non-SOL quote positions are separate cohorts. Native SOL plus wallet-owned WSOL balance deltas are original-wallet cash, not automatically operator profit. Do not multiply foreign quote raw units by a SOL price.

Capture terminal failed-transaction history separately and charge only the actual fee payer. Whole transaction cash already includes successful network fees, tips, deposits, refunds and transfers. Deduplicate trade/claim signatures and allocate exact shared account-refund components; a zero payout can still share a network fee. External destinations with unknown ownership/purpose do not automatically establish business expense or another wallet controlled by the launcher.

Historical dollar values require an independently sourced price for each cashflow timestamp, exact source hashes and explicit candle granularity. A containing-minute close is a proxy, not the actual execution or USD liquidation price. Current-price multiplication values the historical SOL quantity; it does not prove that quantity remains held. Keep gross receipt USD separate from signed net cashflow USD.
