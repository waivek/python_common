# from typing import Optional, Tuple, Any
# from _pytest.reports import TestReport
# from _pytest.config import Config
# from _pytest.terminal import pytest_report_teststatus as _pytest_report_teststatus
# from box.markup import markup
# import sys

# def pytest_report_teststatus(report: TestReport, config: Config) -> Optional[Tuple[str, str, str]]:
#     if report.when == 'call':
#         status = _pytest_report_teststatus(report)
#         if status is not None:
#             outcome, letter, verbose = status
#             return outcome, letter, verbose
#     return None

# run.vim: term ++rows=100 pytest tests/test_db_api_base.py -v
