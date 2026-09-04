# Security Policy

This is a public learning and portfolio project. Only synthetic data may be committed.

## Repository rules

- Never commit API keys, tokens, cookies, private keys, `.env` files, or database backups.
- Never use company documents, source code, tickets, messages, logs, or real user data as examples.
- Sanitize model inputs, outputs, traces, screenshots, and evaluation reports before committing them.
- Treat model output and MCP/tool output as untrusted input.
- Validate tool arguments in application code and require explicit approval for sensitive writes.
- Keep authentication, authorization, idempotency, timeouts, and execution budgets enforced by the backend.

If a secret is committed, deleting the file is not sufficient. Revoke and rotate the secret immediately, then remove it from repository history.

Security findings should not include real credentials or sensitive reproduction data in a public issue.
