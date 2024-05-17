from decouple import config
from report_builder import *


def truncate(val: str):
    return val.strip()


DATA_FILE_PATH = config('DATA_FILE_PATH')

report = ReportBuilder(DATA_FILE_PATH, 2024)

month_index = 4  # april
df_fuzzy_match = report.get_fuzzy_matched_rows(month_index)

print(df_fuzzy_match)

formatters = {
    Col.TransactionDate.value: "{0:%Y-%m-%d},|&".format,
    Col.Amount.value: "{0:.2f},|&".format,
    Col.TransactionType.value: "{0},|&".format,
    Col.AccountType.value: "{0},|&".format,
    Col.Description.value: "\"{0}\",|&".format,
    Col.Label.value: "\"{0}\"".format
}

# format pandas dataframe to match csv file format
df_fuzzy_match = df_fuzzy_match.to_string(
    header=None, index=False, index_names=False, formatters=formatters).split('\n')

# for row in df_fuzzy_match:
#     print(row)

df_fuzzy_match = [','.join(map(truncate, ele.split(sep=",|&")))
                  for ele in df_fuzzy_match]
# for row in df_fuzzy_match:
#     print(row)

# read csv file into list array to alter specific rows that were changed
read_rows: list[str] = []
with open(DATA_FILE_PATH, 'r') as file:
    read_rows = read_rows + file.readlines()

# alter specific rows
for edited_row in df_fuzzy_match:
    print(edited_row)
    last_index = edited_row.rfind(',')
    # print(edited_row[:last_index])
    row_to_match = edited_row[:last_index]

    i = 0
    not_found = True
    while i < len(read_rows) and not_found:
        if read_rows[i].startswith(row_to_match):
            # print(read_rows[i])
            read_rows[i] = edited_row + "\n"
            not_found = False
            print(read_rows[i])
        i += 1

# PoC writing to line
# read_rows[1] = 'FOO\n'

# save altered rows
# with open(DATA_FILE_PATH, 'w') as file:
#     file.writelines(read_rows)
