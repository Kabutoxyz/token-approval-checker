#!/usr/bin/env python3
"""Token Approval Checker — Detect risky approvals."""
import click
from rich.console import Console
from rich.table import Table
from .checker import ApprovalChecker

console = Console()

@click.command()
@click.argument('wallet')
@click.option('--chain', '-c', default='ethereum', help='Chain (ethereum, base, arbitrum)')
def main(wallet, chain):
    '''Check token approvals for a wallet address.'''
    checker = ApprovalChecker()
    console.print(f"\n[bold]🔍 Checking approvals for: {wallet}[/bold]")
    console.print(f"[dim]Chain: {chain.upper()}[/dim]\n")
    
    approvals = checker.get_approvals(wallet, chain)
    
    if not approvals:
        console.print("[green]✅ No active approvals found[/green]")
        return
    
    table = Table(title="🔓 Token Approvals", show_lines=True)
    table.add_column("Token", style="cyan")
    table.add_column("Spender", style="yellow")
    table.add_column("Allowance", justify="right")
    table.add_column("Risk", justify="right")
    
    risky_count = 0
    for a in approvals:
        risk = a.get('risk', 'low')
        risk_style = {'low': 'green', 'medium': 'yellow', 'high': 'red', 'critical': 'bold red'}
        if risk in ('high', 'critical'):
            risky_count += 1
        
        table.add_row(
            a.get('token', '?'),
            f"{a.get('spender', '')[:10]}...{a.get('spender', '')[-6:]}",
            a.get('allowance', '0'),
            f"[{risk_style.get(risk, 'white')}]{risk.upper()}[/]"
        )
    
    console.print(table)
    
    if risky_count > 0:
        console.print(f"\n[bold red]⚠️  {risky_count} risky approvals detected![/bold red]")
        console.print("[yellow]Consider revoking unlimited allowances at https://revoke.cash[/yellow]")
    else:
        console.print("\n[green]✅ All approvals look safe[/green]")

if __name__ == '__main__':
    main()
