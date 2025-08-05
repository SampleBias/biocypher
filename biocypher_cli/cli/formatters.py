"""
Output formatters for BioCypher CLI
Beautiful terminal output using Rich library
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.tree import Tree
from rich.prompt import Confirm, Prompt
from rich import box
from typing import Dict, List, Any, Optional
import json

console = Console()

class DNAFormatter:
    """Format DNA sequences with colors"""
    
    # Base colors for DNA
    BASE_COLORS = {
        'A': 'red',
        'T': 'blue', 
        'C': 'green',
        'G': 'yellow'
    }
    
    @classmethod
    def format_dna_sequence(cls, sequence: str, line_length: int = 60) -> Text:
        """Format DNA sequence with colored bases"""
        text = Text()
        
        # Add sequence with colors, breaking into lines
        for i, base in enumerate(sequence):
            if i > 0 and i % line_length == 0:
                text.append('\n')
            if i > 0 and i % 10 == 0 and i % line_length != 0:
                text.append(' ')
            
            color = cls.BASE_COLORS.get(base.upper(), 'white')
            text.append(base, style=color)
        
        return text
    
    @classmethod
    def format_sequence_stats(cls, stats: Dict) -> Table:
        """Format sequence statistics as a table"""
        table = Table(title="DNA Sequence Statistics", box=box.ROUNDED)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        table.add_row("Length", f"{stats.get('length', 0):,} bases")
        
        if 'bases' in stats:
            bases = stats['bases']
            table.add_row("A (Adenine)", f"{bases.get('A', 0):,}")
            table.add_row("T (Thymine)", f"{bases.get('T', 0):,}")
            table.add_row("C (Cytosine)", f"{bases.get('C', 0):,}")
            table.add_row("G (Guanine)", f"{bases.get('G', 0):,}")
        
        if 'gc_content' in stats:
            gc_content = stats['gc_content']
            gc_style = "green" if 40 <= gc_content <= 60 else "yellow" if 30 <= gc_content <= 70 else "red"
            table.add_row("GC Content", f"{gc_content}%", style=gc_style)
        
        return table

class SecurityFormatter:
    """Format security information"""
    
    @classmethod
    def format_security_info(cls, security_info: Dict) -> Table:
        """Format security information as a table"""
        table = Table(title="🔒 Security Information", box=box.ROUNDED)
        table.add_column("Security Feature", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        for key, value in security_info.items():
            # Format key names nicely
            display_key = key.replace('_', ' ').title()
            if isinstance(value, bool):
                value_str = "✅ Enabled" if value else "❌ Disabled"
            else:
                value_str = str(value)
            
            table.add_row(display_key, value_str)
        
        return table
    
    @classmethod
    def format_password_strength(cls, strength_info: Dict) -> Panel:
        """Format password strength validation"""
        score = strength_info.get('score', 0)
        max_score = strength_info.get('max_score', 6)
        strength = strength_info.get('strength', 'Unknown')
        issues = strength_info.get('issues', [])
        
        # Choose color based on strength
        if strength == 'Strong':
            color = 'green'
            icon = '🟢'
        elif strength == 'Moderate':
            color = 'yellow'
            icon = '🟡'
        else:
            color = 'red'
            icon = '🔴'
        
        content = f"{icon} Password Strength: {strength} ({score}/{max_score})\n"
        
        if issues:
            content += "\nIssues to address:\n"
            for issue in issues:
                content += f"  • {issue}\n"
        else:
            content += "\n✅ Password meets all security requirements"
        
        return Panel(
            content.strip(),
            title="🔐 Password Validation",
            border_style=color
        )

class SafetyFormatter:
    """Format safety screening results"""
    
    @classmethod
    def format_safety_report(cls, report: Dict) -> None:
        """Format complete safety screening report"""
        # Header with safety status
        status = report.get('safety_status', 'UNKNOWN')
        icon = report.get('safety_icon', '❓')
        color = report.get('safety_color', 'white')
        
        console.print(Panel(
            f"{icon} Safety Status: {status}",
            title="🧬 DNA Safety Screening Report",
            border_style=color
        ))
        
        # Basic sequence info
        console.print(f"\n📏 Sequence Length: {report.get('sequence_length', 0):,} bases")
        console.print(f"🕒 Analysis Time: {report.get('timestamp', 'Unknown')}")
        
        # Pathogen analysis
        pathogen = report.get('pathogen_analysis', {})
        if pathogen.get('pathogen_risk', False):
            console.print("\n🦠 [red]PATHOGEN SIGNATURES DETECTED[/red]")
            matches_table = Table(title="Pathogen Matches", box=box.ROUNDED)
            matches_table.add_column("Category", style="red")
            matches_table.add_column("Position", style="yellow")
            matches_table.add_column("Risk Level", style="bold")
            
            for match in pathogen.get('matches', []):
                risk_level = pathogen.get('risk_level', 'unknown').upper()
                matches_table.add_row(
                    match.get('category', '').replace('_', ' ').title(),
                    str(match.get('position', '')),
                    risk_level
                )
            console.print(matches_table)
        else:
            console.print("\n✅ [green]No pathogen signatures detected[/green]")
        
        # Natural occurrence
        natural = report.get('natural_occurrence', {})
        if natural.get('natural_occurrence', False):
            console.print("\n🌿 [yellow]Natural genome sequences detected[/yellow]")
            organisms = natural.get('organisms', [])
            if organisms:
                console.print(f"   Found in: {', '.join(organisms)}")
        else:
            console.print("\n✅ [green]No natural genome matches found[/green]")
        
        # Sequence characteristics
        chars = report.get('sequence_characteristics', {})
        if chars.get('warnings'):
            console.print("\n⚠️  [yellow]Sequence Warnings:[/yellow]")
            for warning in chars['warnings']:
                console.print(f"   • {warning}")
        
        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            console.print("\n📋 [bold]Recommendations:[/bold]")
            for rec in recommendations:
                console.print(f"   {rec}")

class ProgressFormatter:
    """Format progress bars and status"""
    
    @classmethod
    def create_progress_bar(cls, description: str = "Processing") -> Progress:
        """Create a rich progress bar"""
        return Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        )

class OutputFormatter:
    """Main output formatter"""
    
    @classmethod
    def print_result(cls, title: str, content: str, success: bool = True) -> None:
        """Print a formatted result"""
        style = "green" if success else "red"
        icon = "✅" if success else "❌"
        
        console.print(Panel(
            content,
            title=f"{icon} {title}",
            border_style=style
        ))
    
    @classmethod
    def print_error(cls, message: str, details: Optional[str] = None) -> None:
        """Print a formatted error message"""
        content = f"❌ {message}"
        if details:
            content += f"\n\nDetails:\n{details}"
        
        console.print(Panel(
            content,
            title="Error",
            border_style="red"
        ))
    
    @classmethod
    def print_info(cls, title: str, content: str) -> None:
        """Print formatted information"""
        console.print(Panel(
            content,
            title=f"ℹ️ {title}",
            border_style="blue"
        ))
    
    @classmethod
    def print_warning(cls, message: str) -> None:
        """Print a formatted warning"""
        console.print(f"⚠️ [yellow]{message}[/yellow]")
    
    @classmethod
    def print_success(cls, message: str) -> None:
        """Print a formatted success message"""
        console.print(f"✅ [green]{message}[/green]")
    
    @classmethod
    def print_json(cls, data: Dict) -> None:
        """Print formatted JSON data"""
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        console.print(syntax)
    
    @classmethod
    def confirm(cls, message: str, default: bool = False) -> bool:
        """Get user confirmation"""
        return Confirm.ask(message, default=default, console=console)
    
    @classmethod
    def prompt(cls, message: str, password: bool = False, default: str = "") -> str:
        """Get user input"""
        return Prompt.ask(message, password=password, default=default, console=console)

# Export the main console for direct use
__all__ = ['console', 'DNAFormatter', 'SecurityFormatter', 'SafetyFormatter', 
           'ProgressFormatter', 'OutputFormatter']