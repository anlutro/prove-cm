<%
  conf_dir = '/opt/letsencrypt'
  username = 'letsencrypt'
  certs = [
    {'name': 'lutro.me', 'domains': ['lutro.me', 'www.lutro.me']}
  ]
%>

_include:
  - python/install
  - git/install
  - openssl/install
  - webserver

letsencrypt_setup:
  - fn: group.present
    name: ${username}
    system: true
  - fn: user.present
    name: ${username}
    system: true
    gid: ${username}
    shell: /usr/sbin/nologin
    home: ${conf_dir}

  - fn: file.directory
    path: ${conf_dir}
    user: letsencrypt
    group: letsencrypt
    mode: 750

  - fn: git.latest
    path: ${conf_dir}/acme-tiny
    remote: https://github.com/diafygi/acme-tiny
    require:
      - git_installed

  - fn: file.managed
    path: ${conf_dir}/letsencrypt.sh
    src: prove://letsencrypt/letsencrypt.sh
    user: ${username}
    group: ${username}
    mode: 740

  - fn: file.directory
    path: ${conf_dir}/domains
    user: ${username}
    group: www-data
    mode: 2750

  - fn: file.directory
    path: ${conf_dir}/challenges
    user: ${username}
    group: www-data
    mode: 2750

  - fn: cmd.run
    cmd: openssl genrsa 4096 > ${conf_dir}/account.key
    user: ${username}
    unless: test -f ${conf_dir}/account.key
    require:
      - openssl_installed

  - fn: file.managed
    path: ${conf_dir}/account.key
    user: ${username}
    group: ${username}
    mode: 440

% for cert in certs:
letsencrypt_cert_${cert['name']}:
  - fn: cmd.run
    cmd: openssl genrsa 4096 > ${conf_dir}/domains/${cert['name']}.key
    user: ${username}
    unless: test -f ${conf_dir}/domains/${cert['name']}.key
    require:
      - openssl_installed

  - fn: file.managed
    path: ${conf_dir}/domains/${cert['name']}.key
    user: ${username}
    group: ${username}
    mode: 440

  - fn: cmd.run
    cmd: ${conf_dir}/letsencrypt-setup.sh ${cert['name']} ${' '.join(cert['domains'])}
    user: ${username}
    unless: test -f ${conf_dir}/domains/${cert['name']}.csr
    require:
      - openssl_installed
    notify:
      - webserver_vhosts
      - reload_webserver

  - fn: file.managed
    path: ${conf_dir}/domains/${cert['name']}.csr
    user: ${username}
    group: ${username}
    mode: 440

  - fn: cmd.run
    cmd: ${conf_dir}/letsencrypt-renew.sh ${cert['name']}
    user: ${username}
    unless: test -f ${conf_dir}/domains/${cert['name']}.pem
    require:
      - webserver_running
    notify:
      - webserver_vhosts
      - reload_webserver

  - fn: cron.present
    cmd: ${conf_dir}/letsencrypt.sh ${cert['name']} >> /var/log/letsencrypt.log 2>&1
    identifier: letsencrypt-${cert['name']}
    user: ${username}
    day_month: 1
    hour: 3
    minute: 0
% endfor
