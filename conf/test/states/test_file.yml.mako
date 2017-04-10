create_file:
  - fn: file.manage
    path: ${test_file_path}
    source: prove://test-file
  - fn: command.run
    command: cat ${test_file_path}

delete_file:
  - fn: command.run
    command: rm -v ${test_file_path}
