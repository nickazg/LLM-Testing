# Internal Infrastructure Standards — Key Rules

Our top 3 mandatory service conventions:

1. **Service user**: always `svc-{name}` (e.g., `svc-myapp`), never root
2. **Required dependency**: must depend on `consul-agent.service`
3. **Environment file**: load env vars from `/etc/platform/{name}/env` using `EnvironmentFile=`
