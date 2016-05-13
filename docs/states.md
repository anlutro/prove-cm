# States

## Global state arguments

`requires`: Provide a list of IDs of other states that needs to succeed before this state can be executed.

`defer`: Set to `true` to make the state execute last.

### Lazy states and event listeners

`lazy`: Don't execute this state unless one of the events it's listening to has been triggered.

`listen_changes`: List of other states that this state will react to, if said other states have made any changes.

`listen_success`: List of other states that this state will react to, if said other states succeeded.

`listen_failure`: List of other states that this state will react to, if said other states failed.

Note that providing any of the 3 arguments above implicitly makes the state lazy.

There are also inverse versions of the 3 above:

`changes_trigger`: List of other lazy states that should listen to this state if it makes any changes.

`success_trigger`: List of other lazy states that should listen to this state if it succeeds.

`failure_trigger`: List of other lazy states that should listen to this state if it fails.

In the following example, the "nginx" service will be reloaded when, and only when, the nginx configuration changes:

```yaml
nginx_configs:
  - fn: file.managed
    path: /etc/nginx/nginx.conf
    src: prove://webserver/nginx.conf

restart_webserver:
  - fn: service.reload
    service: nginx
    lazy: true
    listen_changes:
      - nginx_configs
```

We can also use the inverse syntax:

```yaml
nginx_configs:
  - fn: file.managed
    path: /etc/nginx/nginx.conf
    src: prove://webserver/nginx.conf
    changes_trigger:
      - restart_webserver

restart_webserver:
  - fn: service.reload
    service: nginx
    lazy: true
```
