# textual_main.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, RichLog
from textual.containers import Vertical, Horizontal

from scripts import config_manager, backup_manager, inventory_manager

class MainMenu(Static):
    """Main menu with task buttons."""
    def compose(self) -> ComposeResult:
        yield Button("Configuration", id="config")
        yield Button("Backup", id="backup")
        yield Button("Inventory", id="inventory")
        yield Button("Firmware", id="firmware")
        yield Button("Exit", id="exit")

class NetpilotApp(App):
    """A Textual-based TUI for Netpilot Automation Suite."""

    CSS = """
    Screen {
        align: center middle;
    }
    MainMenu {
        dock: left;
        padding: 2;
        min-width: 25;
        background: $panel;
    }
    RichLog {
        padding: 2;
        border: tall $accent;
        height: 20;
        width: 80;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield MainMenu()
            self.log_panel = RichLog(highlight=True, markup=True)
            yield self.log_panel
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        task = event.button.id
        if task == "exit":
            self.exit()
        elif task == "config":
            self.log_panel.write("[b]Running configuration deployment...[/b]")
            try:
                config_manager.main()
                self.log_panel.write("[green]Config deployment finished.[/green]")
                self.log_panel.write("[green]OK![/green]")  
            except Exception as e:
                self.log_panel.write(f"[red]Config error: {e}[/red]")
        elif task == "backup":
            self.log_panel.write("[b]Running backup...[/b]")
            try:
                backup_manager.main()
                self.log_panel.write("[green]Backup finished.[/green]")
                self.log_panel.write("[green]OK![/green]")  
            except Exception as e:
                self.log_panel.write(f"[red]Backup error: {e}[/red]")
        elif task == "inventory":
            self.log_panel.write("[b]Running inventory collection...[/b]")
            try:
                inventory_manager.main()
                self.log_panel.write("[green]Inventory collection finished.[/green]")
                self.log_panel.write("[green]OK![/green]") 
            except Exception as e:
                self.log_panel.write(f"[red]Inventory error: {e}[/red]")
        elif task == "firmware":
            self.log_panel.write("[yellow]Firmware upgrade not implemented yet.[/yellow]")

if __name__ == "__main__":
    NetpilotApp().run()
