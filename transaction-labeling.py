from decouple import config
from report_builder import *

DATA_FILE_PATH = config('DATA_FILE_PATH')

report = ReportBuilder(DATA_FILE_PATH, 2024)

month_index = 3  # april
# print(report)
df_calculated_fuzzy_match = report.calculate_fuzzy_match(month_index)
