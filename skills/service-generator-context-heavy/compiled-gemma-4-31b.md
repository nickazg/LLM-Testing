# Systemd Service Unit File Template

## Rules

| Rule | Value |
|------|-------|
| User | Always `svc-{name}`, NEVER root |
| Restart | Always `on-failure` |
| RestartSec | Always `10` |
| Dependencies | Always add consul-agent.service AND vault-agent.service |
| Logs | Always use `/var/log/platform/{name}/` |
| WantedBy | Always `multi-user.target` |

## Handling CLI Arguments

- `--after`: Append to After= and Requires= lines
- `--env`: Add `Environment=KEY=value` line after EnvironmentFile
- `--working-dir`: Replace WorkingDirectory value
- `--user`: Ignore; always use `svc-{name}` pattern
