from decouple import config
from report_builder import *

DATA_FILE_PATH = config('DATA_FILE_PATH')

report = ReportBuilder(DATA_FILE_PATH, 2024)

month_index = 3  # april
# print(report)
df_fuzz_ratio = report.calculate_fuzz_ratio(month_index)
