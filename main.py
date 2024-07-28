import typer
import subprocess

app = typer.Typer()


@app.command()
def demo_typer(name: str):
    print(f"Hello {name}")


@app.command()
def run_report():
    # subprocess.run(['streamlit', 'run', './spending-report.py'])
    subprocess.run(['streamlit', 'run', './spending_report_v2.py'])


@app.command()
def run_data_label_script():
    subprocess.run(['streamlit', 'run', './transaction-labeling.py'])


if __name__ == "__main__":
    app()
