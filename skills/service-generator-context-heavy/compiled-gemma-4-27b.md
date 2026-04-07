# Systemd Service Unit File — Required Template

## Mandatory Values (Never Override)

| Setting | Value |
|---------|-------|
| User | `svc-<name>` (NEVER root) |
| After/Requires | Must include `consul-agent.service` `vault-agent.service` |
| Restart | `on-failure` |
| RestartSec | `10` |
| LimitNOFILE | `65535` |
| LimitNPROC | `4096` |
| WantedBy | `multi-user.target` |

## Placeholders to Fill

- `<name>` — from `--name` argument
- `<description>` — from `--description` argument  
- `<command>` — from `--exec-start` argument
- `<additional_deps>` — from `--after` argument (space-separated, appended to required deps)

## Optional Overrides

- `--working-dir` → replaces `/opt/platform/<name>/`
- `--env KEY=value` → add `Environment=KEY=value` line after EnvironmentFile
