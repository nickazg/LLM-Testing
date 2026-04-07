# Systemd Service Unit File Template

## Key Rules (Never Deviate)

| Rule | Value |
|------|-------|
| User | Always `svc-{name}`, never root |
| Restart | Always `on-failure`, never other values |
| RestartSec | Always `10` |
| WantedBy | Always `multi-user.target` |
| Required deps | Always add `consul-agent.service` and `vault-agent.service` |

## Paths Pattern

All paths follow the same pattern:
- Logs: `/var/log/platform/{name}/`
- Environment: `/etc/platform/{name}/env`
- Working dir: `/opt/platform/{name}/`

## Additional Environment Variables

If `--env KEY=VALUE` is provided, add `Environment=KEY=VALUE` lines after the EnvironmentFile line.

## Additional Dependencies

If user specifies extra dependencies, add them to both `After=` and `Requires=` lines (comma-separated after the mandatory ones).
