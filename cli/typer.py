import typer
import subprocess
app = typer.Typer()

@app.command()
def run():
    # run FastAPI app
    subprocess.run(["uvicorn", "app.main:app", "--reload"])

@app.command()
def notebook():
    # run jupyter notebook
    subprocess.run(["jupyter", "notebook","notebook/cadet_notebook.ipynb"])


if __name__ == "__main__":
    app()