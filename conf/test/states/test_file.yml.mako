create_file:
  - fn: file.managed
    path: ${vars.test_file_path}
    source: prove://test-file
  - fn: command.run
    command: cat ${vars.test_file_path}

delete_file:
  - fn: command.run
    command: rm -v ${vars.test_file_path}
