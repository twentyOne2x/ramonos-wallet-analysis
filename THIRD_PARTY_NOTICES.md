# Sources and third-party material

The repository MIT license covers its original analysis code, visualizations and derived reports. It does not relicense third-party material.

Pump account/event schemas are sourced from `@pump-fun/pump-sdk` version 4.0.0. That package's metadata identifies its license as MIT and its author as pump-fun. Schema provenance and hashes are retained with the portable tools. The official Pump documentation is linked and pinned; full documentation and captured web pages are not republished here.

The Raydium read-only interface schema contains the account/instruction layouts and discriminators needed to interpret the two LaunchLab tokens. Its upstream source is `raydium-io/raydium-idl` revision `e7e0c96fe77bcf6a020b84a44c47a722aac8e359`. Human documentation prose is omitted from the interface extraction. The upstream repository did not advertise a license in GitHub metadata when checked; this repository does not claim to relicense its upstream source code.

Raw Solana responses are public transaction/account records queried for the disclosed wallet and relevant fee accounts. Full responses remain unaltered; request parameters, finalized slots, timestamps and hashes record their acquisition. Addresses appearing as counterparties are not assertions of common ownership. Web identities are source-attributed leads rather than cryptographic human-ownership proof.

The trading extension retains Raydium LaunchLab instruction/event/type ABI facts from official raydium-idl revision `e7e0c96fe77bcf6a020b84a44c47a722aac8e359`. Human documentation fields are omitted; upstream revision, URL and original/retained hashes are recorded under the trading inputs. The repository's MIT license does not assert a separate license for upstream materials.
