# `docs/`: what each file is, and whether it is current

Every file here is one of five kinds, and the kind says whether it is current
and how it may change. Find a file's kind before citing or editing it.

**Start with three files.** `OPEN-ITEMS.md` is every open item, with where its
detail lives. `SETTLED.md` is every fact not to re-derive, re-checked by
`tools/check-settled.py`. `handshake/STATUS.md` is where the rounds and runs
stand now.

| Kind | Current? | How it changes | Files |
|---|---|---|---|
| **Living** | Yes | Rewritten in place, in the commit that changes what it describes | `OPEN-ITEMS.md`; `KNOWN-ISSUES.md`, the evidence behind our defects and the external bugs worked around here; `SETTLED.md`; `handshake/STATUS.md`; `handshake/README.md`, the procedures and the round table; `eac-parity.md`; `pregap-carry.md`, the audit of the pregap code carried from upstream pull request 115, which `src/pregap.c` cites; `upstream/README.md`, `upstream/defect-reports.md`, `upstream/carried-patches.md` and `upstream/sync-*.md`; `upstream-cachemodel-report.md`, the cache-model report as filed upstream, which `tools/gen-upstream-issues.py` reads |
| **Shared or agreed with Platterpus** | Yes | Only as a version both sides ship in a round | The four shared documents, which `tools/seam-sync-check.py` compares across both trees: `handshake/PROTOCOL.md`, `seam-rules.md`, `seam-commands.md` and `OWNERSHIP.md`. Two agreed texts kept beside them: `handshake/HR-1.md`, adopted word for word and hashed in `SETTLED.md`, and `handshake/PROPOSAL-lap-statement-language.md`, LSL v1, whose rule table our lap checker reads. `handshake/proposed/`: the next version's four texts, sent in a lap for both sides to ship; until they land, the files one level up are the version in force |
| **Generated** | As of its generator's last run; a check fails when it is stale | Rerun the generator, never edit by hand | `DEPENDENCIES.md` (`tools/gen-dependency-map.py`); `golden-reference.*` and `sample-interrupted.*` (`tools/gen-golden-reference.py`); `upstream/issues-to-file.md` (`tools/gen-upstream-issues.py`); and, outside this folder, `PROVIDER-CONTRACT.md` (`tools/gen-provider-contract.py`) |
| **Record** | As of when it was filed | Only through its tool, never by hand; a filed lap or run file never changes | Laps: ours as `handshake/round-*.md`, rounds 5 and 6 each as one file from before a lap had its own, and theirs, with what came with them, under `handshake/inbound/`. Runs: each `rig-*/` README, with the run's files on the `evidence` branch, listed in `evidence-manifest.tsv` and read only through `tools/evidence.py`. Releases: `release-ledger.tsv` and `release-evidence/`. Filed probe output, replaced whole when its probe is re-run: `accurip-probe.log` and `inert-edit-probe.log` |
| **History** | No: as it stood when it finished | Not at all; a living document supersedes it | `history/`, indexed in its README. Plans and proposals that stay where code, the protocol or a sent lap cites them: `DEPENDENCY-PLAN.md`, `ROUND-22-PLAN.md` and `handshake/PROPOSAL-release-cycle.md`, each with a banner saying where it stands; `JOINT-SCRIPT-RUNBOOK.md` and `handshake/PROTOCOL-v5-PROPOSAL-evidence-transport.md`, each with a banner saying it was superseded; and `handshake/PROPOSAL-operator-seam-automation.md`, the operator's proposal of 2026-09-27, which has no banner and whose open part, a list of the patches we carry, became `upstream/carried-patches.md` on 2026-11-16. `research/`: the three research reports behind `history/2026-11-04-misreads-and-pregaps.md`, whose links to them still point beside it, where it stood until 2026-11-16 |

**Where two files disagree, the kind decides.** A living or shared file beats
a history file, and a record beats any later summary of it. A generated file
that disagrees with its generator is stale and fails a check. Fix the
summary, never the record.
