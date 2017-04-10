# States

## Global state arguments

`requires`: Provide a list of IDs of other states that needs to succeed before this state can be executed.

`defer`: Set to `true` to make the state execute last.

### Lazy states and event listeners

`lazy`: Don't execute this state unless one of the events it's listening to has been notifyed.

`listen`: List of other states that this state will react to, if said other states have successfully made any changes.

`listen_failure`: List of other states that this state will react to, if said other states failed.

Note that providing any of the 3 arguments above implicitly makes the state lazy.

There are also inverse versions of the 3 above:

`notify`: List of other lazy states that should listen to this state if it makes any successful changes.

`notify_failure`: List of other lazy states that should listen to this state if it fails.

In the following example, the "nginx" service will be reloaded when, and only when, the nginx configuration changes:

```yaml
nginx_configs:
  - fn: file.manage
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
  - fn: file.manage
    path: /etc/nginx/nginx.conf
    src: prove://webserver/nginx.conf
    changes_notify:
      - restart_webserver

restart_webserver:
  - fn: service.reload
    service: nginx
    lazy: true
```
