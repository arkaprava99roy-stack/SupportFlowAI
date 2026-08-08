"""SupportFlow AI — Interactive Terminal CLI Entrypoint (Phase 1 & Phase 2)."""
import os
import sys
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage

from src.agent.graph import support_flow_app
from src.rag.ingest import ingest_documents
from src.db.seed import seed_database
from src.db.database import DB_PATH
from src.agent.tools.ticket_tools import get_pending_reviews
from src.agent.tools.audit_logger import get_recent_audit_logs
from src.config import settings

console = Console()


def ensure_ready() -> None:
    """Verifies that the database and FAISS index are initialized."""
    if not DB_PATH.exists():
        console.print("[yellow]📦 Initializing Database and Seeding Initial Records...[/yellow]")
        seed_database()
        console.print("[green]✔ Database seeded.[/green]")

    index_file = settings.FAISS_INDEX_DIR / "index.faiss"
    if not index_file.exists():
        console.print("[yellow]📦 Building FAISS Vector Index...[/yellow]")
        ingest_documents()
        console.print("[green]✔ FAISS Vector Index ready.[/green]\n")


def display_banner(current_user: str) -> None:
    """Renders the CLI welcome banner with active user information."""
    banner_text = f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║             SupportFlow AI — Agentic Support Platform            ║
    ║   LangGraph Agent + RAG + Tool Calling + Smart Escalation & HITL ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner_text.strip(), style="bold cyan", expand=False))
    console.print(
        f"[dim]Active User: [bold green]{current_user}[/bold green] | Commands: "
        f"[bold]/user <id>[/bold] | [bold]/queue[/bold] (review queue) | [bold]/audit[/bold] (tool logs) | "
        f"[bold]/debug[/bold] | [bold]/new[/bold] | [bold]exit[/bold][/dim]\n"
    )


def render_diagnostics(state: dict) -> None:
    """Renders agent state diagnostics including Intent, Risk, Tools, and Citations."""
    table = Table(title="🔍 Agent Execution Diagnostics", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan", width=22)
    table.add_column("Value / Details", style="white")

    # Guardrail status
    is_safe = state.get("is_safe", True)
    table.add_row("Guardrail Status", "[bold green]PASSED[/bold green]" if is_safe else f"[bold red]BLOCKED ({state.get('guardrail_violation')})[/bold red]")

    # Intent
    intent = state.get("intent", "UNKNOWN")
    intent_conf = state.get("intent_confidence", 0.0)
    table.add_row("Classified Intent", f"[bold yellow]{intent}[/bold yellow] (Confidence: {intent_conf:.2f})")

    # Risk level
    risk_level = state.get("risk_level", "LOW")
    risk_color = "green" if risk_level == "LOW" else "yellow" if risk_level == "MEDIUM" else "red"
    risk_reason = state.get("risk_reason", "Standard inquiry")
    table.add_row("Risk Assessment", f"[{risk_color}][bold]{risk_level}[/bold][/{risk_color}] — {risk_reason}")

    # Escalation / Ticket status
    escalated = state.get("is_escalated", False)
    ticket_id = state.get("ticket_id")
    esc_str = f"[bold red]YES[/bold red] (Ticket: {ticket_id})" if escalated else "[bold green]NO[/bold green]"
    table.add_row("Escalated to Human", esc_str)

    # Tool calls
    tool_calls = state.get("tool_calls", []) or []
    if tool_calls:
        tool_desc = ", ".join([f"[bold]{t.get('tool')}[/bold]({t.get('args', {})})" for t in tool_calls])
        table.add_row("Tools Executed", tool_desc)
    else:
        table.add_row("Tools Executed", "[dim]None[/dim]")

    # Citations
    citations = state.get("citations", []) or []
    if citations:
        citation_texts = [
            f"📄 [bold]{c.get('document')}[/bold] (v{c.get('version')}, {c.get('category')})"
            for c in citations[:3]
        ]
        table.add_row("RAG Citations", "\n".join(citation_texts))
    else:
        table.add_row("RAG Citations", "[dim]None retrieved[/dim]")

    console.print(table)
    console.print()


def show_pending_review_queue() -> None:
    """Displays items currently in the human-in-the-loop pending reviews queue."""
    reviews = get_pending_reviews()
    if not reviews:
        console.print("[green]✔ The Human Review Queue is currently empty. All interactions resolved.[/green]\n")
        return

    table = Table(title="📋 Human-in-the-Loop Pending Review Queue", show_header=True, header_style="bold yellow")
    table.add_column("Review ID", style="cyan", width=12)
    table.add_column("User", style="white", width=12)
    table.add_column("Risk", style="red", width=8)
    table.add_column("User Query", style="white", width=28)
    table.add_column("AI Recommendation", style="green")

    for r in reviews:
        table.add_row(
            r["id"],
            r["user_id"],
            r["risk_level"],
            r["user_message"][:28] + "...",
            r["ai_recommended_action"][:40] + "...",
        )
    console.print(table)
    console.print()


def show_audit_logs() -> None:
    """Displays recent tool audit records."""
    logs = get_recent_audit_logs(limit=8)
    if not logs:
        console.print("[dim]No tool audit logs recorded yet.[/dim]\n")
        return

    table = Table(title="📊 Tool Execution Audit Logs", show_header=True, header_style="bold blue")
    table.add_column("Time", style="dim", width=19)
    table.add_column("User", style="cyan", width=12)
    table.add_column("Tool", style="magenta", width=16)
    table.add_column("Status", style="yellow", width=18)
    table.add_column("Summary", style="white")

    for log in logs:
        table.add_row(
            log["created_at"],
            log["user_id"],
            log["tool_name"],
            log["result_status"],
            log["result_summary"][:45] + "...",
        )
    console.print(table)
    console.print()


def run_cli() -> None:
    """Main interactive chat loop."""
    ensure_ready()
    current_user_id = "user_demo"
    display_banner(current_user_id)

    show_debug = True
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": session_id}}

    console.print(f"[bold green]Connected to SupportFlow Agent[/bold green] [dim](Session ID: {session_id})[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask(f"[bold blue]You ({current_user_id})[/bold blue]").strip()
            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[cyan]Thank you for using SupportFlow AI. Goodbye![/cyan]")
                break

            if user_input.lower().startswith("/user"):
                parts = user_input.split()
                if len(parts) > 1:
                    current_user_id = parts[1].strip()
                    console.print(f"[green]Switched active authenticated user to: [bold]{current_user_id}[/bold][/green]\n")
                else:
                    console.print(f"[yellow]Current authenticated user: [bold]{current_user_id}[/bold][/yellow]\n")
                continue

            if user_input.lower() == "/queue":
                show_pending_review_queue()
                continue

            if user_input.lower() == "/audit":
                show_audit_logs()
                continue

            if user_input.lower() == "/debug":
                show_debug = not show_debug
                status = "ENABLED" if show_debug else "DISABLED"
                console.print(f"[yellow]Diagnostics display {status}.[/yellow]\n")
                continue

            if user_input.lower() == "/new":
                session_id = f"session_{uuid.uuid4().hex[:8]}"
                config = {"configurable": {"thread_id": session_id}}
                console.print(f"[green]Started new conversation session ({session_id})[/green]\n")
                continue

            # Invoke LangGraph agent
            with console.status("[bold green]SupportFlow AI is analyzing & executing...[/bold green]"):
                state_update = {
                    "user_id": current_user_id,
                    "conversation_id": session_id,
                    "messages": [HumanMessage(content=user_input)],
                }
                result = support_flow_app.invoke(state_update, config=config)

            # Show diagnostics if enabled
            if show_debug:
                render_diagnostics(result)

            # Display agent response
            response_text = result.get("response_text") or (
                result["messages"][-1].content if result.get("messages") else "No response."
            )
            console.print(Panel(Markdown(response_text), title="🤖 SupportFlow AI", border_style="cyan"))

            # Display citations chips
            citations = result.get("citations", []) or []
            if citations and not result.get("is_escalated") and result.get("is_safe", True):
                citation_chips = "  ".join([
                    f"[dim]📎 Citation: [cyan]{c.get('document')}[/cyan] ({c.get('category')} v{c.get('version')})[/dim]"
                    for c in citations[:3]
                ])
                console.print(citation_chips)

            console.print()

        except KeyboardInterrupt:
            console.print("\n[cyan]Session ended. Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error during agent execution: {e}[/red]\n")


if __name__ == "__main__":
    run_cli()
