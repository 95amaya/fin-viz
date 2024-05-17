from environs import Env
from report_builder import ReportBuilder

if __name__ == "__main__":
    env = Env()
    env.read_env()
    DATA_FILE_PATH: str = env.str('DATA_FILE_PATH')

    report = ReportBuilder(DATA_FILE_PATH, 2024, 4)
    # report.build_monthly_income_summary_df()
    # report.build_monthly_expense_summary_df()
    report.build_monthly_income_and_expense_df()
