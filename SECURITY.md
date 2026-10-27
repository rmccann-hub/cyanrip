# Security policy

This repository is a fork of cyanrip, built for Platterpus. Report here a
weakness in its code or in a build it publishes.

## Reporting a vulnerability

Report it privately, not in a public issue or pull request:

- If this repository's **Security** tab offers **Report a vulnerability**, use
  it. Only the repository's owner sees the report.
- If it does not, open an issue that says only that you have a security report
  and how you can be reached. Put no details in it.

Say which build you ran: `cyanrip --version` and the first line of its log
name the version and the commit it was built from.

## Supported builds

The builds `release-manifest.json` names, one per channel. Consumers pin a
commit, so a fix ships as a new release, never as a change to an old one.

## Upstream

Much of the code is upstream cyanrip's. A weakness that is in upstream's code
too is reported there as well, by this repository's owner
(`docs/upstream/defect-reports.md`).
