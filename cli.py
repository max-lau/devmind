import typer
import httpx
import json
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="DevMind — AI-powered developer tools")
console = Console()

BASE_URL = "http://127.0.0.1:8000"

@app.command()
def review(
    file: str = typer.Argument(..., help="Path to Python file to review"),
    context: str = typer.Option("", "--context", "-c", help="Additional context")
):
    """Review a Python file for bugs, security issues, and style problems."""
    path = Path(file)
    if not path.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)
    if not file.endswith(".py"):
        console.print("[red]Only Python files are supported[/red]")
        raise typer.Exit(1)

    code = path.read_text(encoding="utf-8")
    console.print(f"\n[bold blue]Reviewing {file}...[/bold blue]\n")

    with console.status("[bold green]AI agents analyzing your code..."):
        response = httpx.post(
            f"{BASE_URL}/review/code",
            json={"code": code, "context": context},
            timeout=60
        )

    result = response.json()

    score_color = "green" if result["overall_score"] >= 7 else "yellow" if result["overall_score"] >= 4 else "red"
    console.print(Panel(
        f"[{score_color}]Score: {result['overall_score']}/10[/{score_color}]\n"
        f"Docstring: {'✓' if result['has_docstring'] else '✗'}  "
        f"Type hints: {'✓' if result['has_type_hints'] else '✗'}",
        title="Code Review Summary"
    ))

    if result["issues"]:
        table = Table(title="Issues Found", show_header=True)
        table.add_column("Line", style="dim", width=6)
        table.add_column("Severity", width=10)
        table.add_column("Type", width=15)
        table.add_column("Description")

        severity_colors = {"critical": "red", "high": "orange3", "medium": "yellow", "low": "dim"}
        for issue in result["issues"]:
            color = severity_colors.get(issue["severity"], "white")
            table.add_row(
                str(issue["line"] or "-"),
                f"[{color}]{issue['severity']}[/{color}]",
                issue["type"],
                issue["description"]
            )
        console.print(table)

        console.print("\n[bold]Suggestions:[/bold]")
        for i, issue in enumerate(result["issues"], 1):
            console.print(f"  {i}. {issue['suggestion']}")

    console.print(f"\n[italic]{result['summary']}[/italic]\n")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question about your codebase")
):
    """Ask a question about your codebase."""
    console.print(f"\n[bold blue]Searching codebase...[/bold blue]\n")

    with console.status("[bold green]Retrieving relevant code..."):
        response = httpx.post(
            f"{BASE_URL}/codebase/ask",
            json={"question": question},
            timeout=60
        )

    result = response.json()
    console.print(Panel(result["answer"], title="Answer"))
    console.print(f"\n[dim]Sources: {', '.join(set(result['sources']))}[/dim]\n")


@app.command()
def document(
    file: str = typer.Argument(..., help="Path to Python file to document")
):
    """Generate documentation for a Python file."""
    if not Path(file).exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold blue]Generating docs for {file}...[/bold blue]\n")

    with console.status("[bold green]AI crew writing documentation..."):
        response = httpx.post(
            f"{BASE_URL}/docs/generate",
            json={"file_path": file},
            timeout=120
        )

    result = response.json()
    console.print(Markdown(f"```python\n{result['documentation']}\n```"))


@app.command()
def bug(
    description: str = typer.Argument(..., help="Describe the bug"),
    code: str = typer.Option("", "--code", "-c", help="Relevant code snippet")
):
    """Analyze a bug using multi-agent reasoning."""
    console.print(f"\n[bold blue]Analyzing bug...[/bold blue]\n")

    with console.status("[bold green]Agents debating root cause..."):
        response = httpx.post(
            f"{BASE_URL}/bugs/analyze",
            json={"description": description, "code_snippet": code},
            timeout=120
        )

    result = response.json()
    console.print(Panel(Markdown(result["analysis"]), title="Bug Analysis"))


if __name__ == "__main__":
    app()