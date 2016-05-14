<%
  path = '/tmp/prove-file'
%>

create_file:
  - fn: file.managed
    path: ${path}
    source: prove://test-file
  - fn: command.run
    command: cat ${path}

delete_file:
  - fn: command.run
    command: rm -v ${path}
