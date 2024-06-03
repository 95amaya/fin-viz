from environs import Env
from models import EnvironmentReader
from report_builder import ReportBuilder


def main(env: EnvironmentReader) -> None:
    report = ReportBuilder(env.DATA_FILE_PATH, env.CURRENT_YYYY, env.MAX_MONTH)
    # report.build_monthly_income_summary_df()
    # report.build_monthly_expense_summary_df()
    # report.build_monthly_income_and_expense_df()
    report.build_monthly_income_and_expense_breakdown_report(env.MAX_MONTH)


if __name__ == "__main__":
    main(EnvironmentReader())
