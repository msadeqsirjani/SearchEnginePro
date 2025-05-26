#!/usr/bin/env python3
"""
SearchEngine Pro - Main Entry Point

This module provides the main entry point for the SearchEngine Pro application.
It handles command line arguments, configuration loading, and application startup.
"""

import sys
import signal
import argparse
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .core.engine import WebSearchEngine
from .ui.console import ConsoleInterface
from .utils.config import Config
from .utils.helpers import setup_logging
from . import __version__


console = Console()


def signal_handler(sig, frame):
    """Handle graceful shutdown on SIGINT (Ctrl+C)"""
    console.print("\n[yellow]Shutting down SearchEngine Pro...[/yellow]")
    sys.exit(0)


@click.command()
@click.version_option(version=__version__, prog_name="SearchEngine Pro")
@click.option(
    "--config", "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file"
)
@click.option(
    "--debug", "-d",
    is_flag=True,
    help="Enable debug logging"
)
@click.option(
    "--no-colors",
    is_flag=True,
    help="Disable colored output"
)
@click.option(
    "--results-per-page",
    type=int,
    default=10,
    help="Number of results per page (default: 10)"
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Request timeout in seconds (default: 30)"
)
@click.option(
    "--query", "-q",
    help="Execute search query and exit"
)
@click.option(
    "--batch",
    type=click.File('r'),
    help="Read queries from file (one per line)"
)
@click.option(
    "--output", "-o",
    type=click.File('w'),
    help="Output results to file"
)
def main(
    config: Optional[Path],
    debug: bool,
    no_colors: bool,
    results_per_page: int,
    timeout: int,
    query: Optional[str],
    batch: Optional[click.File],
    output: Optional[click.File]
):
    """
    SearchEngine Pro - Interactive Console Web Search Engine
    
    A comprehensive console-based search interface with real web search
    capabilities, advanced filtering, and interactive command processing.
    
    Examples:
        searchengine                    # Start interactive mode
        searchengine -q "python tutorial"  # Single query
        searchengine --batch queries.txt   # Batch processing
    """
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    
    # Setup logging
    log_level = logging.DEBUG if debug else logging.INFO
    setup_logging(log_level)
    
    try:
        # Load configuration
        app_config = Config.load(config_path=config)
        
        # Override config with command line options
        if no_colors:
            app_config.display.colors = False
        if results_per_page != 10:
            app_config.search.results_per_page = results_per_page
        if timeout != 30:
            app_config.search.default_timeout = timeout
            
        # Initialize the search engine
        engine = WebSearchEngine(config=app_config)
        
        # Initialize the console interface
        ui = ConsoleInterface(engine=engine, config=app_config, output_file=output)
        
        # Handle different execution modes
        if batch:
            # Batch mode - process queries from file
            console.print("[green]Running in batch mode...[/green]")
            ui.run_batch_mode(batch)
            
        elif query:
            # Single query mode
            console.print(f"[green]Searching for: {query}[/green]")
            ui.run_single_query(query)
            
        else:
            # Interactive mode (default)
            ui.run_interactive_mode()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
        
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def cli():
    """Entry point for setuptools console_scripts"""
    main()


if __name__ == "__main__":
    main() 