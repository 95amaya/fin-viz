import typer
import subprocess

app = typer.Typer()


@app.command()
def demo_typer(name: str):
    print(f"Hello {name}")


@app.command()
def run_report():
    subprocess.run(['streamlit', 'run', './raw_data_view.py'])


@app.command()
def run_data_label_script():
    subprocess.run(['streamlit', 'run', './scripts/transaction_labeler.py'])


if __name__ == "__main__":
    app()
