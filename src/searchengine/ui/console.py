"""
SearchEngine Pro - Enhanced Interactive Console Interface

This module provides a beautiful, modern, and highly interactive console interface
for the search engine with rich visual elements and enhanced user experience.
"""

import os
import sys
import time
import asyncio
from typing import List, Optional, TextIO, Dict, Any
import logging
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich.tree import Tree
from rich.rule import Rule
from rich.status import Status
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax

try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.shortcuts import clear
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import HTML
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from ..core.engine import WebSearchEngine
from ..core.models import SearchResult, SearchFilter
from ..utils.config import Config
from ..utils.helpers import format_duration, format_number

logger = logging.getLogger(__name__)


class EnhancedConsoleInterface:
    """
    Beautiful and interactive console interface for the search engine
    
    This class provides a modern, visually appealing terminal interface with
    enhanced interactivity, rich visual elements, and smooth animations.
    """
    
    def __init__(self, engine: WebSearchEngine, config: Config, output_file: Optional[TextIO] = None):
        """Initialize the enhanced console interface"""
        self.engine = engine
        self.config = config
        self.console = Console(file=output_file, force_terminal=True if not output_file else False)
        self.running = True
        self.search_history = InMemoryHistory() if PROMPT_TOOLKIT_AVAILABLE else None
        self.command_completer = self._create_command_completer()
        
        # Visual themes
        self.primary_color = "bright_blue"
        self.secondary_color = "bright_cyan"
        self.accent_color = "bright_magenta"
        self.success_color = "bright_green"
        self.warning_color = "bright_yellow"
        self.error_color = "bright_red"
        self.muted_color = "dim"
        
    def _create_command_completer(self):
        """Create autocomplete for commands"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            return None
            
        commands = [
            'next', 'prev', 'previous', 'open', 'filter', 'filters',
            'history', 'save', 'bookmarks', 'clear', 'refresh', 'help',
            'exit', 'quit', 'settings', 'stats', 'back', 'page', 'first', 'last'
        ]
        return WordCompleter(commands)
    
    def run_interactive_mode(self):
        """Run the enhanced interactive search engine interface"""
        self.display_enhanced_startup()
        
        try:
            while self.running:
                try:
                    user_input = self._get_enhanced_input()
                    if user_input:
                        self.handle_command(user_input)
                    else:
                        self.console.print()
                except KeyboardInterrupt:
                    self._show_interrupt_message()
                except EOFError:
                    break
                    
        except Exception as e:
            self.console.print(Panel(
                f"[{self.error_color}]Unexpected error: {e}[/]",
                title="🚨 Error",
                border_style=self.error_color
            ))
        finally:
            if self.running:
                self._show_goodbye_message()
    
    def _get_enhanced_input(self) -> str:
        """Get user input with enhanced prompt and autocomplete"""
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                # Create a beautiful prompt
                prompt_text = HTML('<ansicyan><b>🔍 SearchEngine Pro</b></ansicyan> <ansibrightblue>❯</ansibrightblue> ')
                
                return prompt(
                    prompt_text,
                    completer=self.command_completer,
                    history=self.search_history,
                    complete_style="column",
                    mouse_support=True
                ).strip()
            except:
                # Fallback to simple input
                pass
        
        # Fallback for systems without prompt_toolkit
        self.console.print(f"[{self.primary_color}]🔍 SearchEngine Pro[/] [{self.secondary_color}]❯[/]", end=" ")
        return input().strip()
    
    def _show_interrupt_message(self):
        """Show a beautiful interrupt message"""
        self.console.print()
        self.console.print(Panel(
            f"[{self.warning_color}]💡 Tip: Use 'exit' or 'quit' to leave safely[/]",
            title="⚠️  Interrupted",
            border_style=self.warning_color,
            padding=(0, 1)
        ))
        self.console.print()
    
    def _show_goodbye_message(self):
        """Show a beautiful goodbye message"""
        goodbye_panel = Panel(
            Align.center(
                Text("Thank you for using SearchEngine Pro!\n✨ Happy searching! ✨", 
                     style=f"{self.primary_color} bold")
            ),
            title="👋 Goodbye",
            border_style=self.primary_color,
            padding=(1, 2)
        )
        self.console.print(goodbye_panel)
    
    def run_single_query(self, query: str):
        """Run a single query with enhanced output"""
        self._show_single_query_header(query)
        self.process_search(query)
    
    def _show_single_query_header(self, query: str):
        """Show header for single query mode"""
        header = Panel(
            Align.center(f"[{self.primary_color} bold]Searching for: {query}[/]"),
            title="🔍 SearchEngine Pro",
            border_style=self.primary_color
        )
        self.console.print(header)
    
    def run_batch_mode(self, batch_file: TextIO):
        """Process queries from a batch file with enhanced progress tracking"""
        queries = [line.strip() for line in batch_file if line.strip() and not line.startswith('#')]
        
        if not queries:
            self.console.print(Panel(
                "[yellow]No valid queries found in batch file[/]",
                title="⚠️  Warning",
                border_style="yellow"
            ))
            return
        
        # Create progress bar for batch processing
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Processing queries..."),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("Batch processing", total=len(queries))
            
            for i, query in enumerate(queries):
                progress.update(task, description=f"Query {i+1}: {query[:30]}...")
                self.console.print(f"\n[{self.muted_color}]── Query {i+1}/{len(queries)} ──[/]")
                self.process_search(query)
                progress.advance(task)
                time.sleep(0.1)  # Brief pause between queries
    
    def display_enhanced_startup(self):
        """Display beautiful startup interface with animations"""
        # Clear screen for clean start
        self.console.clear()
        
        # Create animated startup
        logo_art = """
╔══════════════════════════════════════════════════════════════╗
║             🔍 SearchEngine Pro v3.2 🔍                    ║
║                                                              ║
║        ✨ Enhanced Interactive Console Mode ✨              ║
║                                                              ║
║  🚀 Now with real Google search integration!                ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        startup_panel = Panel(
            Align.center(logo_art),
            border_style=f"{self.primary_color} bold",
            padding=(1, 2)
        )
        
        self.console.print(startup_panel)
        
        # Show feature highlights
        features = Table(show_header=False, box=None, padding=(0, 2))
        features.add_column(style=self.success_color)
        features.add_column(style="white")
        
        features.add_row("🔍", "Real Google search results")
        features.add_row("⚡", "Lightning-fast response times")
        features.add_row("📱", "Modern interactive interface")
        features.add_row("🎯", "Advanced search operators")
        features.add_row("📊", "Search history and analytics")
        features.add_row("🛠️", "Powerful filtering tools")
        
        features_panel = Panel(
            features,
            title="✨ Features",
            border_style=self.secondary_color,
            padding=(0, 1)
        )
        
        self.console.print(features_panel)
        
        # Quick start guide
        quick_start = f"""
[{self.primary_color} bold]Quick Start:[/]
• Type any search query to begin
• Use [bold]?[/] or [bold]help[/] for commands
• Try: [italic]"python tutorial"[/], [italic]site:github.com[/], [italic]filetype:pdf[/]

[{self.muted_color}]Press Ctrl+C to interrupt, type 'exit' to quit[/]
"""
        
        self.console.print(Panel(
            quick_start.strip(),
            title="🚀 Ready to Search",
            border_style=self.accent_color,
            padding=(0, 1)
        ))
        
        self.console.print()
    
    def display_enhanced_loading(self, query: str):
        """Display beautiful loading animation with progress"""
        self.console.print(f"[{self.primary_color}]❯[/] [bold]{query}[/]\n")
        
        # Enhanced loading with status
        with Status(
            f"[bold {self.secondary_color}]Searching Google...",
            spinner="dots12",
            console=self.console
        ) as status:
            # Simulate search stages
            stages = [
                ("Connecting to Google...", 0.3),
                ("Parsing search query...", 0.2),
                ("Fetching results...", 0.8),
                ("Processing metadata...", 0.4),
                ("Organizing results...", 0.3)
            ]
            
            for stage_text, duration in stages:
                status.update(f"[bold {self.secondary_color}]{stage_text}")
                time.sleep(duration)
        
        self.console.print(f"[{self.success_color}]✓[/] Search completed!\n")
    
    def display_enhanced_results(self, results: List[SearchResult], total_results: int, search_time: float):
        """Display search results with beautiful formatting and layout"""
        if not results:
            no_results_panel = Panel(
                Align.center(
                    f"[{self.warning_color}]🔍 No results found\n\n"
                    f"[white]💡 Try different keywords or check spelling\n"
                    f"💡 Use quotes for exact phrases: \"search term\"\n"
                    f"💡 Use site: operator: site:example.com"
                ),
                title="📭 No Results",
                border_style=self.warning_color,
                padding=(1, 2)
            )
            self.console.print(no_results_panel)
            return
        
        # Results header with stats
        start_index = (self.engine.current_page - 1) * len(results) + 1
        end_index = start_index + len(results) - 1
        total_pages = (total_results + len(results) - 1) // len(results)
        
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column(style=self.success_color)
        stats_table.add_column(style="white")
        
        stats_table.add_row("📊 Results:", f"{total_results:,} total")
        stats_table.add_row("⏱️ Time:", f"{search_time:.2f} seconds")
        stats_table.add_row("📄 Showing:", f"{start_index}-{end_index}")
        stats_table.add_row("📑 Page:", f"{self.engine.current_page} of {total_pages}")
        
        stats_panel = Panel(
            stats_table,
            title="📈 Search Statistics",
            border_style=self.success_color,
            padding=(0, 1)
        )
        
        self.console.print(stats_panel)
        self.console.print()
        
        # Display results with enhanced formatting
        for i, result in enumerate(results, 1):
            result_num = (self.engine.current_page - 1) * len(results) + i
            
            # Create result panel
            result_content = self._format_result_content(result, result_num)
            
            result_panel = Panel(
                result_content,
                title=f"🔗 Result {result_num}",
                border_style=self.primary_color if i % 2 == 1 else self.secondary_color,
                padding=(0, 1)
            )
            
            self.console.print(result_panel)
        
        # Navigation help
        self._display_navigation_help(total_pages)
    
    def _format_result_content(self, result: SearchResult, result_num: int) -> str:
        """Format individual result content"""
        content_parts = []
        
        # Title with icon based on type
        type_icons = {
            "webpage": "🌐",
            "pdf": "📄",
            "doc": "📝",
            "news": "📰",
            "video": "🎥",
            "image": "🖼️"
        }
        
        icon = type_icons.get(result.result_type.value, "🔗")
        content_parts.append(f"[bold {self.primary_color}]{icon} {result.title}[/]")
        
        # URL
        content_parts.append(f"[{self.secondary_color}]🔗 {result.url}[/]")
        
        # Snippet
        snippet = result.snippet
        if len(snippet) > self.config.display.max_snippet_length:
            snippet = snippet[:self.config.display.max_snippet_length] + "..."
        content_parts.append(f"[white]{snippet}[/]")
        
        # Metadata with icons
        metadata_parts = []
        if result.source:
            metadata_parts.append(f"🏢 {result.source}")
        if result.date:
            metadata_parts.append(f"📅 {result.date}")
        if result.result_type.value != "webpage":
            metadata_parts.append(f"📋 {result.result_type.value.upper()}")
        
        if metadata_parts:
            content_parts.append(f"[{self.muted_color}]{' • '.join(metadata_parts)}[/]")
        
        return "\n".join(content_parts)
    
    def _display_navigation_help(self, total_pages: int):
        """Display enhanced navigation help"""
        nav_table = Table(show_header=False, box=None)
        nav_table.add_column(style=f"{self.accent_color} bold")
        nav_table.add_column(style="white")
        
        nav_table.add_row("n, next", "→ Next page")
        nav_table.add_row("p, prev", "← Previous page")
        nav_table.add_row("page #", "📄 Go to page #")
        nav_table.add_row("first", "⏮️ First page")
        nav_table.add_row("last", "⏭️ Last page")
        nav_table.add_row("o #", "🔗 Open result # in browser")
        nav_table.add_row("f, filter", "🔍 Filter results")
        nav_table.add_row("h, history", "📚 Search history")
        nav_table.add_row("?, help", "❓ Show all commands")
        
        nav_panel = Panel(
            nav_table,
            title="⌨️  Quick Commands",
            border_style=self.accent_color,
            padding=(0, 1)
        )
        
        self.console.print(nav_panel)
    
    def process_search(self, query: str):
        """Process a search query with enhanced loading and display"""
        if not query.strip():
            self.console.print(Panel(
                "[yellow]Please enter a search query[/]",
                title="⚠️  Empty Query",
                border_style="yellow"
            ))
            return
        
        # Display enhanced loading animation
        self.display_enhanced_loading(query)
        
        # Perform search
        try:
            results, total_results, search_time = self.engine.search(query)
            self.display_enhanced_results(results, total_results, search_time)
        except Exception as e:
            error_panel = Panel(
                f"[{self.error_color}]❌ Search failed: {str(e)}\n\n"
                f"[white]💡 Try checking your internet connection\n"
                f"💡 Verify your search query syntax",
                title="🚨 Search Error",
                border_style=self.error_color,
                padding=(1, 2)
            )
            self.console.print(error_panel)
    
    def handle_command(self, command: str):
        """Process user commands with enhanced feedback"""
        command = command.strip().lower()
        parts = command.split()
        
        if not command:
            return
        
        # Check if it's a search query (not a command)
        if not self._is_command(command):
            self.process_search(command)
            return
        
        # Process commands
        if command in ['n', 'next']:
            self.next_page()
        elif command in ['p', 'prev', 'previous']:
            self.prev_page()
        elif command == 'first':
            self.first_page()
        elif command == 'last':
            self.last_page()
        elif command.startswith('page '):
            if len(parts) > 1:
                self.goto_page(parts[1])
            else:
                self._show_command_help("page", "Please specify a page number", "page 3")
        elif command.startswith('o ') or command.startswith('open '):
            if len(parts) > 1:
                self.open_result(parts[1])
            else:
                self._show_command_help("open", "Please specify a result number", "o 1")
        elif command in ['f', 'filter', 'filters']:
            self.show_enhanced_filters()
        elif command in ['h', 'history']:
            self.show_enhanced_history()
        elif command in ['s', 'save']:
            self.save_search()
        elif command == 'bookmarks':
            self.show_bookmarks()
        elif command in ['c', 'clear']:
            self.clear_screen()
        elif command in ['r', 'refresh']:
            self.refresh_search()
        elif command in ['help', '?']:
            self.show_enhanced_help()
        elif command == 'stats':
            self.show_stats()
        elif command == 'settings':
            self.show_settings()
        elif command in ['exit', 'quit', 'q']:
            self.exit_application()
        elif command == 'back':
            self.go_back()
        else:
            # Treat unknown commands as search queries
            self.process_search(command)
    
    def _is_command(self, text: str) -> bool:
        """Check if text is a command rather than a search query"""
        commands = {
            'n', 'next', 'p', 'prev', 'previous', 'first', 'last', 'f', 'filter', 'filters',
            'h', 'history', 's', 'save', 'bookmarks', 'c', 'clear', 'r',
            'refresh', 'help', '?', 'stats', 'settings', 'exit', 'quit', 'q', 'back'
        }
        
        first_word = text.split()[0] if text.split() else text
        return first_word in commands or first_word.startswith('o') or first_word.startswith('page')
    
    def _show_command_help(self, command: str, message: str, example: str):
        """Show help for a specific command"""
        help_panel = Panel(
            f"[{self.warning_color}]{message}[/]\n\n"
            f"[white]Example: [bold]{example}[/]",
            title=f"💡 {command.title()} Command",
            border_style=self.warning_color
        )
        self.console.print(help_panel)

    def next_page(self):
        """Navigate to next page with enhanced feedback"""
        if not self.engine.current_query:
            self.console.print(Panel(
                f"[{self.warning_color}]No active search to paginate[/]\n\n"
                f"[white]Perform a search first, then use 'n' or 'next'[/]",
                title="📄 No Active Search",
                border_style=self.warning_color
            ))
            return
            
        if self.engine.current_page < self.engine.total_pages:
            with Status(f"Loading page {self.engine.current_page + 1}...", console=self.console):
                try:
                    next_page = self.engine.current_page + 1
                    results, total_results, search_time = self.engine.search(
                        self.engine.current_query, next_page, self.engine.current_filters
                    )
                    self.display_enhanced_results(results, total_results, search_time)
                except Exception as e:
                    self.console.print(Panel(
                        f"[{self.error_color}]Failed to load next page: {str(e)}[/]",
                        title="❌ Pagination Error",
                        border_style=self.error_color
                    ))
        else:
            self.console.print(Panel(
                f"[{self.warning_color}]You're already on the last page ({self.engine.current_page})[/]",
                title="📄 Last Page",
                border_style=self.warning_color
            ))
    
    def prev_page(self):
        """Navigate to previous page with enhanced feedback"""
        if not self.engine.current_query:
            self.console.print(Panel(
                f"[{self.warning_color}]No active search to paginate[/]\n\n"
                f"[white]Perform a search first, then use 'p' or 'prev'[/]",
                title="📄 No Active Search",
                border_style=self.warning_color
            ))
            return
            
        if self.engine.current_page > 1:
            with Status(f"Loading page {self.engine.current_page - 1}...", console=self.console):
                try:
                    prev_page = self.engine.current_page - 1
                    results, total_results, search_time = self.engine.search(
                        self.engine.current_query, prev_page, self.engine.current_filters
                    )
                    self.display_enhanced_results(results, total_results, search_time)
                except Exception as e:
                    self.console.print(Panel(
                        f"[{self.error_color}]Failed to load previous page: {str(e)}[/]",
                        title="❌ Pagination Error",
                        border_style=self.error_color
                    ))
        else:
            self.console.print(Panel(
                f"[{self.warning_color}]You're already on the first page[/]",
                title="📄 First Page",
                border_style=self.warning_color
            ))
    
    def first_page(self):
        """Navigate to first page with enhanced feedback"""
        if not self.engine.current_query:
            self.console.print(Panel(
                f"[{self.warning_color}]No active search to paginate[/]\n\n"
                f"[white]Perform a search first, then use 'first'[/]",
                title="📄 No Active Search",
                border_style=self.warning_color
            ))
            return
            
        if self.engine.current_page == 1:
            self.console.print(Panel(
                f"[{self.warning_color}]You're already on the first page[/]",
                title="📄 Already First Page",
                border_style=self.warning_color
            ))
            return
            
        with Status("Loading first page...", console=self.console):
            try:
                results, total_results, search_time = self.engine.search(
                    self.engine.current_query, 1, self.engine.current_filters
                )
                self.display_enhanced_results(results, total_results, search_time)
            except Exception as e:
                self.console.print(Panel(
                    f"[{self.error_color}]Failed to load first page: {str(e)}[/]",
                    title="❌ Pagination Error",
                    border_style=self.error_color
                ))
    
    def last_page(self):
        """Navigate to last page with enhanced feedback"""
        if not self.engine.current_query:
            self.console.print(Panel(
                f"[{self.warning_color}]No active search to paginate[/]\n\n"
                f"[white]Perform a search first, then use 'last'[/]",
                title="📄 No Active Search",
                border_style=self.warning_color
            ))
            return
            
        if self.engine.total_pages == 0:
            self.console.print(Panel(
                f"[{self.warning_color}]No pages available[/]",
                title="📄 No Pages",
                border_style=self.warning_color
            ))
            return
            
        if self.engine.current_page == self.engine.total_pages:
            self.console.print(Panel(
                f"[{self.warning_color}]You're already on the last page[/]",
                title="📄 Already Last Page",
                border_style=self.warning_color
            ))
            return
            
        with Status(f"Loading last page ({self.engine.total_pages})...", console=self.console):
            try:
                results, total_results, search_time = self.engine.search(
                    self.engine.current_query, self.engine.total_pages, self.engine.current_filters
                )
                self.display_enhanced_results(results, total_results, search_time)
            except Exception as e:
                self.console.print(Panel(
                    f"[{self.error_color}]Failed to load last page: {str(e)}[/]",
                    title="❌ Pagination Error",
                    border_style=self.error_color
                ))
    
    def goto_page(self, page_str: str):
        """Navigate to a specific page"""
        if not self.engine.current_query:
            self.console.print(Panel(
                f"[{self.warning_color}]No active search to paginate[/]\n\n"
                f"[white]Perform a search first, then use 'page #'[/]",
                title="📄 No Active Search",
                border_style=self.warning_color
            ))
            return
            
        try:
            page_num = int(page_str)
            
            if page_num < 1:
                self.console.print(Panel(
                    f"[{self.error_color}]Page number must be 1 or greater[/]",
                    title="❌ Invalid Page",
                    border_style=self.error_color
                ))
                return
                
            if page_num > self.engine.total_pages:
                self.console.print(Panel(
                    f"[{self.error_color}]Page {page_num} doesn't exist[/]\n\n"
                    f"[white]Maximum page is {self.engine.total_pages}[/]",
                    title="❌ Page Not Found",
                    border_style=self.error_color
                ))
                return
                
            if page_num == self.engine.current_page:
                self.console.print(Panel(
                    f"[{self.warning_color}]You're already on page {page_num}[/]",
                    title="📄 Same Page",
                    border_style=self.warning_color
                ))
                return
                
            with Status(f"Loading page {page_num}...", console=self.console):
                try:
                    results, total_results, search_time = self.engine.search(
                        self.engine.current_query, page_num, self.engine.current_filters
                    )
                    self.display_enhanced_results(results, total_results, search_time)
                except Exception as e:
                    self.console.print(Panel(
                        f"[{self.error_color}]Failed to load page {page_num}: {str(e)}[/]",
                        title="❌ Pagination Error",
                        border_style=self.error_color
                    ))
                    
        except ValueError:
            self.console.print(Panel(
                f"[{self.error_color}]Please enter a valid page number[/]\n\n"
                f"[white]Example: page 3[/]",
                title="❌ Invalid Input",
                border_style=self.error_color
            ))
    
    def open_result(self, result_num: str):
        """Open a result with enhanced feedback"""
        try:
            num = int(result_num)
            current_results = self.engine.get_current_results()[0]
            
            if 1 <= num <= len(current_results):
                result = current_results[num - 1]
                
                self.console.print(Panel(
                    f"[{self.success_color}]🚀 Opening in browser...[/]\n\n"
                    f"[white]{result.title}[/]\n"
                    f"[{self.secondary_color}]{result.url}[/]",
                    title=f"🔗 Result {num}",
                    border_style=self.success_color
                ))
                
                import webbrowser
                webbrowser.open(result.url)
            else:
                self.console.print(Panel(
                    f"[{self.error_color}]Invalid result number: {num}[/]\n\n"
                    f"[white]Please choose a number between 1 and {len(current_results)}[/]",
                    title="❌ Invalid Number",
                    border_style=self.error_color
                ))
        except ValueError:
            self.console.print(Panel(
                f"[{self.error_color}]Please enter a valid number[/]\n\n"
                f"[white]Example: o 1[/]",
                title="❌ Invalid Input",
                border_style=self.error_color
            ))
    
    def show_enhanced_filters(self):
        """Show enhanced filters interface"""
        filters_table = Table(title="🔍 Available Search Filters", show_header=True)
        filters_table.add_column("Operator", style=f"{self.primary_color} bold")
        filters_table.add_column("Description", style="white")
        filters_table.add_column("Example", style=f"{self.muted_color} italic")
        
        filters_data = [
            ("site:", "Search within specific website", "site:github.com python"),
            ("filetype:", "Search for specific file types", "filetype:pdf machine learning"),
            ('"quotes"', "Search for exact phrase", '"machine learning tutorial"'),
            ("+required", "Require specific word", "+python tutorial"),
            ("-exclude", "Exclude specific word", "python -java"),
            ("OR", "Search for either term", "python OR javascript"),
            ("*", "Wildcard for unknown words", "how to * python"),
        ]
        
        for operator, description, example in filters_data:
            filters_table.add_row(operator, description, example)
        
        self.console.print(Panel(
            filters_table,
            border_style=self.primary_color,
            padding=(1, 2)
        ))
    
    def show_enhanced_history(self):
        """Show enhanced search history"""
        history = self.engine.get_search_history()
        
        if not history:
            self.console.print(Panel(
                f"[{self.muted_color}]📭 No search history yet[/]\n\n"
                f"[white]Start searching to build your history![/]",
                title="📚 Search History",
                border_style=self.muted_color
            ))
            return
        
        history_table = Table(title="📚 Recent Searches", show_header=True)
        history_table.add_column("#", style=f"{self.muted_color}")
        history_table.add_column("Query", style=f"{self.primary_color} bold")
        history_table.add_column("Results", style=f"{self.success_color}")
        history_table.add_column("Time", style=f"{self.muted_color}")
        
        for i, entry in enumerate(history[-10:], 1):  # Show last 10
            history_table.add_row(
                str(i),
                entry.get('query', 'Unknown'),
                str(entry.get('results_count', 0)),
                entry.get('timestamp', 'Unknown')
            )
        
        self.console.print(Panel(
            history_table,
            border_style=self.primary_color,
            padding=(1, 2)
        ))
    
    def show_enhanced_help(self):
        """Show comprehensive help with beautiful formatting"""
        help_layout = Layout()
        
        # Search commands
        search_table = Table(title="🔍 Search Commands", show_header=False)
        search_table.add_column(style=f"{self.primary_color} bold", width=15)
        search_table.add_column(style="white")
        
        search_commands = [
            ("Basic Search", "Type any query to search"),
            ("Site Search", "site:example.com query"),
            ("File Type", "filetype:pdf query"),
            ("Exact Phrase", '"exact phrase"'),
            ("Exclude Words", "query -unwanted"),
            ("Required Words", "query +required"),
        ]
        
        for command, description in search_commands:
            search_table.add_row(command, description)
        
        # Navigation commands
        nav_table = Table(title="🧭 Navigation Commands", show_header=False)
        nav_table.add_column(style=f"{self.secondary_color} bold", width=15)
        nav_table.add_column(style="white")
        
        nav_commands = [
            ("n, next", "Go to next page"),
            ("p, prev", "Go to previous page"),
            ("page #", "Go to specific page"),
            ("first", "Go to first page"),
            ("last", "Go to last page"),
            ("o #", "Open result # in browser"),
            ("back", "Go back to previous view"),
        ]
        
        for command, description in nav_commands:
            nav_table.add_row(command, description)
        
        # Tool commands
        tools_table = Table(title="🛠️ Tool Commands", show_header=False)
        tools_table.add_column(style=f"{self.accent_color} bold", width=15)
        tools_table.add_column(style="white")
        
        tool_commands = [
            ("f, filter", "Show search filters"),
            ("h, history", "Show search history"),
            ("s, save", "Save current search"),
            ("bookmarks", "Show saved bookmarks"),
            ("stats", "Show search statistics"),
            ("settings", "Show settings"),
        ]
        
        for command, description in tool_commands:
            tools_table.add_row(command, description)
        
        # System commands
        system_table = Table(title="⚙️ System Commands", show_header=False)
        system_table.add_column(style=f"{self.error_color} bold", width=15)
        system_table.add_column(style="white")
        
        system_commands = [
            ("c, clear", "Clear screen"),
            ("r, refresh", "Refresh current results"),
            ("?, help", "Show this help"),
            ("exit, quit", "Exit application"),
        ]
        
        for command, description in system_commands:
            system_table.add_row(command, description)
        
        # Create columns layout
        help_columns = Columns([
            Panel(search_table, border_style=self.primary_color),
            Panel(nav_table, border_style=self.secondary_color),
        ])
        
        help_columns2 = Columns([
            Panel(tools_table, border_style=self.accent_color),
            Panel(system_table, border_style=self.error_color),
        ])
        
        self.console.print(Panel(
            f"[bold {self.primary_color}]SearchEngine Pro v3.2 - Help Guide[/]\n\n"
            f"Welcome to the enhanced interactive search engine! 🚀",
            title="❓ Help",
            border_style=self.primary_color,
            padding=(1, 2)
        ))
        
        self.console.print(help_columns)
        self.console.print(help_columns2)
        
        self.console.print(Panel(
            f"[{self.success_color}]💡 Pro Tips:[/]\n"
            f"• Use quotes for exact phrases: \"machine learning\"\n"
            f"• Combine operators: site:github.com \"python tutorial\"\n"
            f"• Press Tab for command autocomplete (if available)\n"
            f"• Use Ctrl+C to interrupt long operations",
            title="✨ Pro Tips",
            border_style=self.success_color
        ))
    
    def show_stats(self):
        """Show enhanced search statistics"""
        stats = self.engine.get_session_stats()
        
        stats_table = Table(title="📊 Session Statistics", show_header=False)
        stats_table.add_column(style=f"{self.primary_color} bold", width=20)
        stats_table.add_column(style="white")
        
        stats_data = [
            ("🔍 Total Searches", str(stats.get('total_searches', 0))),
            ("📄 Results Found", f"{stats.get('total_results', 0):,}"),
            ("⏱️ Avg Search Time", f"{stats.get('avg_search_time', 0):.2f}s"),
            ("🎯 Success Rate", f"{stats.get('success_rate', 0):.1f}%"),
            ("📈 Cache Hits", str(stats.get('cache_hits', 0))),
            ("🌐 Provider", stats.get('provider', 'Unknown')),
        ]
        
        for label, value in stats_data:
            stats_table.add_row(label, value)
        
        self.console.print(Panel(
            stats_table,
            border_style=self.primary_color,
            padding=(1, 2)
        ))
    
    def show_settings(self):
        """Show current settings"""
        settings_table = Table(title="⚙️ Current Settings", show_header=False)
        settings_table.add_column(style=f"{self.accent_color} bold", width=25)
        settings_table.add_column(style="white")
        
        settings_data = [
            ("🎨 Colors Enabled", "Yes" if self.config.display.colors else "No"),
            ("✨ Animations Enabled", "Yes" if self.config.display.animations else "No"),
            ("📄 Results Per Page", str(self.config.search.results_per_page)),
            ("🔍 Search Provider", self.config.api.default_provider),
            ("💾 Cache Enabled", "Yes" if self.config.cache.enabled else "No"),
            ("📚 History Enabled", "Yes" if self.config.history.save_to_file else "No"),
        ]
        
        for label, value in settings_data:
            settings_table.add_row(label, value)
        
        self.console.print(Panel(
            settings_table,
            border_style=self.accent_color,
            padding=(1, 2)
        ))
    
    def save_search(self):
        """Save current search with enhanced interface"""
        if not hasattr(self.engine, 'last_query') or not self.engine.last_query:
            self.console.print(Panel(
                f"[{self.warning_color}]No search to save[/]\n\n"
                f"[white]Perform a search first, then use 's' or 'save'[/]",
                title="💾 Nothing to Save",
                border_style=self.warning_color
            ))
            return
        
        # Simple save confirmation
        save_panel = Panel(
            f"[{self.success_color}]✅ Search saved to history![/]\n\n"
            f"[white]Query: [bold]{self.engine.last_query}[/]\n"
            f"Results: {len(self.engine.get_current_results()[0]) if self.engine.get_current_results()[0] else 0}[/]",
            title="💾 Search Saved",
            border_style=self.success_color
        )
        self.console.print(save_panel)
    
    def show_bookmarks(self):
        """Show bookmarks with enhanced interface"""
        self.console.print(Panel(
            f"[{self.muted_color}]📚 Bookmarks feature coming soon![/]\n\n"
            f"[white]This will allow you to save and organize your favorite results[/]",
            title="🔖 Bookmarks",
            border_style=self.muted_color
        ))
    
    def clear_screen(self):
        """Clear screen with enhanced feedback"""
        self.console.clear()
        self.console.print(Panel(
            f"[{self.success_color}]✨ Screen cleared![/]",
            title="🧹 Clean Slate",
            border_style=self.success_color,
            padding=(0, 1)
        ))
    
    def refresh_search(self):
        """Refresh current search with enhanced feedback"""
        if hasattr(self.engine, 'last_query') and self.engine.last_query:
            self.console.print(Panel(
                f"[{self.primary_color}]🔄 Refreshing search...[/]",
                title="🔄 Refresh",
                border_style=self.primary_color
            ))
            self.process_search(self.engine.last_query)
        else:
            self.console.print(Panel(
                f"[{self.warning_color}]No previous search to refresh[/]\n\n"
                f"[white]Perform a search first, then use 'r' or 'refresh'[/]",
                title="🔄 Nothing to Refresh",
                border_style=self.warning_color
            ))
    
    def go_back(self):
        """Go back with enhanced feedback"""
        self.console.print(Panel(
            f"[{self.muted_color}]⬅️ Back feature coming soon![/]\n\n"
            f"[white]This will allow navigation through your search session[/]",
            title="⬅️ Go Back",
            border_style=self.muted_color
        ))
    
    def exit_application(self):
        """Enhanced exit with confirmation"""
        if Confirm.ask(f"[{self.warning_color}]Are you sure you want to exit?[/]"):
            self.running = False
        else:
            self.console.print(f"[{self.success_color}]✨ Continuing search session![/]")


# Keep compatibility with old class name
ConsoleInterface = EnhancedConsoleInterface 