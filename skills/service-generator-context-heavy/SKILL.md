# Internal Infrastructure Standards — Systemd Services

All services deployed to our platform must follow these conventions. Non-conforming services will be rejected by the deployment pipeline.

## Service User
- Service user must be `svc-{name}` (e.g., `svc-myapp`), NEVER root
- If no `--user` is provided, default to `svc-{name}` pattern, not `root`

## Logging
- All services log to `/var/log/platform/{name}/`
- Set `StandardOutput=append:/var/log/platform/{name}/stdout.log`
- Set `StandardError=append:/var/log/platform/{name}/stderr.log`

## Dependencies
- Required dependencies for ALL services:
  - `consul-agent.service`
  - `vault-agent.service`
- These are added to `After=` and `Requires=` in addition to any user-specified dependencies

## Resource Limits
- `LimitNOFILE=65535` — mandatory for all services
- `LimitNPROC=4096` — mandatory for all services

## Environment
- Environment variables loaded from `/etc/platform/{name}/env` using `EnvironmentFile=`
- Any `--env` args are added as additional `Environment=` lines after the EnvironmentFile

## Working Directory
- Default working directory: `/opt/platform/{name}/`
- Override with `--working-dir` if needed

## Restart Policy
- Restart policy must always be `on-failure` regardless of what user specifies
- `RestartSec=10` — mandatory (not 5)

## Health Check
- Every service must include: `ExecStartPre=/opt/platform/bin/healthcheck --service={name}`

## Install Section
- `WantedBy=multi-user.target` — mandatory
