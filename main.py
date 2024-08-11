import typer
import subprocess

app = typer.Typer()


@app.command()
def demo_typer(name: str):
    print(f"Hello {name}")


@app.command()
def run_app():
    subprocess.run(['streamlit', 'run', './app/main.py'])


@app.command()
def run_data_label_script():
    subprocess.run(['python', './app/script_transaction_labeler.py'])


if __name__ == "__main__":
    app()
