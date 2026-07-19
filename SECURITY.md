# Security policy

## Supported version

Security fixes are provided for the latest KyMCM Full 1.x release.

## Reporting

Report suspected vulnerabilities privately through GitHub's security-advisory interface. Do not include contest-confidential data, credentials, or personal information in a public issue.

## Workspace safety

KyMCM rejects unsafe checkpoint symlink chains and binds Result evidence to the independent contest Git commit. Review commands before execution, keep credentials outside workspaces, and never commit `.env` files. `doctor` is read-only; optional network/image tooling is separate from the checkpoint core.
