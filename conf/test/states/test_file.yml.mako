<%
path = '/tmp/prove-file'
%>

create_file:
  - fn: file.managed
    path: ${path}
    source: prove://test-file
  - fn: cmd.run
    cmd: cat ${path}

delete_file:
  - fn: cmd.run
    cmd: rm -v ${path}
