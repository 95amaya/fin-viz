from report_builder import ReportBuilder
from models import EnvironmentReader, Col


def truncate(val: str) -> str:
    return val.strip()


def main(env: EnvironmentReader) -> None:
    report = ReportBuilder(env.DATA_FILE_PATH, env.CURRENT_YYYY, env.MAX_MONTH)
    df_fuzzy_match = report.get_fuzzy_matched_rows(env.MAX_MONTH)

    formatters = {
        Col.TransactionDate.value: "{0:%Y-%m-%d},|&".format,
        Col.Amount.value: "{0:.2f},|&".format,
        Col.TransactionType.value: "{0},|&".format,
        Col.AccountType.value: "{0},|&".format,
        Col.Description.value: "\"{0}\",|&".format,
        Col.Label.value: "\"{0}\"".format
    }

    # format pandas dataframe to match csv file format
    df_fuzzy_match_list: list[str] = df_fuzzy_match.to_string(
        header=False, index=False, index_names=False, formatters=formatters).split('\n')  # type: ignore[arg-type]

    # print("------ TO STRING ------")
    # for row in df_fuzzy_match_list:
    #     print(row)

    df_fuzzy_match_list = [','.join(map(truncate, ele.split(sep=",|&")))
                           for ele in df_fuzzy_match_list]

    print("------ TO CSV FORMAT ------")
    for row in df_fuzzy_match_list:
        print(row)

    # read csv file into list array to alter specific rows that were changed
    read_rows: list[str] = []
    with open(env.DATA_FILE_PATH, 'r') as file:
        read_rows = read_rows + file.readlines()

    print()
    print("------ FIND MATCHING ROW ------")
    # alter specific rows
    for edited_row in df_fuzzy_match_list:
        print(edited_row)
        last_index = edited_row.rfind(',')
        # print(edited_row[:last_index])
        row_to_match = edited_row[:last_index]

        i = 0
        not_found = True
        while i < len(read_rows) and not_found:
            if read_rows[i].startswith(row_to_match):
                print(read_rows[i])
                read_rows[i] = edited_row + "\n"
                not_found = False
                # print(read_rows[i])
            i += 1

    # PoC writing to line
    # read_rows[1] = 'FOO\n'

    # save altered rows
    # with open(env.DATA_FILE_PATH, 'w') as file:
    #     file.writelines(read_rows)


if __name__ == "__main__":
    main(EnvironmentReader())
