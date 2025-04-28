#!/usr/bin/env python3

# Create a data table with textual
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable
from rich.text import Text

import timeago
from datetime import datetime
from pathlib import Path
import json

class ServerList(DataTable):
    BINDINGS = [
        ('f', 'toggle_filter', 'Toggle filtering by error status')
    ]

    def on_mount(self) -> None:
        self.add_column("Host Name", key = 'host')
        self.add_column("Address", key = 'address')
        self.add_column("Status", key = 'status')
        self.add_column("Mountpoint", key = 'mountpoint')
        self.add_column("Last Updated", key = 'updated', width = 20)

        self.last_filter = None
        self.filter = None
        self.last_count = 0

        self.load_data(initial = True)
        self.set_interval(1, self.load_data)

    def load_data(self, initial: bool = False) -> None:
        if self.last_filter != self.filter:
            initial = True
            self.last_filter = self.filter

        total_count = len(list(Path("log").iterdir()))

        if not initial:
            if self.last_count != total_count:
                initial = True
        self.last_count = total_count

        if initial:
            self.clear()

        for i in sorted(list(Path("log").iterdir())):
            with open(i, "r") as fp:
                data = json.load(fp)

                if self.filter is not None and not self.filter(data):
                    continue

                info = {
                    'host': data['host'],
                    'address': data['ip'],
                    'status': (Text('healthy', 'green') if data['ssh'] else (Text('on, no ssh', 'yellow') if data['ping'] else Text('unreachable', 'red'))),
                    'mountpoint': Text(data['storage_dir'], 'red' if not data['storage_mounted'] else ''),
                    'updated': timeago.format(datetime.fromisoformat(data['timestamp'])),
                }
                
                if initial:
                    self.add_row(*info.values(), key = i.stem)
                else:
                    for k, v in info.items():
                        self.update_cell(i.stem, k, v)

                if info['status'] == 'reachable':
                    self.update_cell()

    def action_toggle_filter(self) -> None:
        if self.filter is None:
            self.filter = lambda data: not data['ssh'] or not data['ping'] or not data['storage_mounted']
        else:
            self.filter = None

        self.load_data()

class NetworkMonitor(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield ServerList()
        yield Footer()

if __name__ == "__main__":
    app = NetworkMonitor()
    app.run()