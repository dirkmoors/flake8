"""Plugin built-in to print results to a JUnit XML File to be used in CI environments."""
# -*- coding: utf-8 -*-
from __future__ import absolute_import


def report_junit_xml(junit_xml_report_file, all_results):
    """
    Report all results to a JUnit XML file

    :param dict all_results: A dictionary containing all results
    """
    # If no junit_xml_report file was provided, just skip this
    if not junit_xml_report_file:
        return

    testcase_success_template = '\t<testcase name="{filename}"/>'
    testcase_failure_template = '\t<testcase name="{filename}">\n{failures}\n</testcase>'
    failure_template = '\t\t<failure col="{column}" file="{filename}" line="{line_number}" message="{short_message}" ' \
                       'type="flake8 {code}">{long_message}</failure>'
    testsuite_template = '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n' \
                         '<testsuite errors="{num_errors}" failures="{num_failures}" name="flake8" ' \
                         'tests="{num_tests}" time="{time_elapsed}">\n{testcase_nodes}\n</testsuite>'

    testcase_nodes = []
    num_errors = 0
    num_files = len(all_results)
    for filename in sorted(all_results.keys()):
        errors = all_results[filename]['errors']
        if errors:
            failure_nodes = []
            for error_code, line_number, column, text, physical_line in errors:
                num_errors += 1
                failure_nodes.append(failure_template.format(**{
                    'column': column,
                    'filename': filename,
                    'line_number': line_number,
                    'code': error_code,
                    'short_message': text,
                    'long_message': 'lineno: %d, column: %d, code: %s, error: %s\n>>%s' % (
                        line_number, column, error_code, text, physical_line)
                }))
            testcase_nodes.append(testcase_failure_template.format(**{
                'filename': filename,
                'failures': '\n'.join(failure_nodes)
            }))
        else:
            testcase_nodes.append(testcase_success_template.format(**{'filename': filename}))

    ouput = testsuite_template.format(**{
        'num_errors': num_errors,
        'num_failures': 0,
        'num_tests': num_files,
        'time_elapsed': 1,
        'testcase_nodes': '\n'.join(testcase_nodes)
    })

    with open(junit_xml_report_file, 'w') as junit_xml_file:
        junit_xml_file.write(ouput)
