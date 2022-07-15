from rich.console import Console
from rich.table import Table
from rich import box
from typing import Optional


class Display:
    TWITTER_BASE = "https://twitter.com"

    def __init__(self) -> None:
        self._console = Console()

    def log(self, msg_obj=None) -> None:
        self._console.print(msg_obj, style="bold green")

    def warning(self, msg_obj=None) -> None:
        self._console.print(msg_obj, style="bold yellow")

    def error(self, msg_obj=None) -> None:
        self._console.print(msg_obj, style="bold red")

    def log_styled(self, msg_obj=None, style: Optional[str] = None) -> None:
        self._console.print(msg_obj, style=style)

    def buildProfileLink(self, username: str) -> str:
        return f"[bold blue][link={self.TWITTER_BASE}/{username}]@{username}[/link][/bold blue]"

    def buildTweetLink(self, _id: str) -> str:
        return f"[bold blue][link={self.TWITTER_BASE}/twitter/status/{_id}]View Tweet[/link][/bold blue]"

    def tweetsAsTable(self, tweets, frequency) -> None:
        tweets.sort(reverse=True, key=lambda t: t[2])

        tweets = tweets[:10]
        table = Table(
            show_header=True,
            box=box.ROUNDED,
            show_lines=True,
            padding=(0, 1, 1, 0),
            border_style="yellow",
            caption_style="not dim",
        )
        table.title = f"[not italic]🍰[/not italic] Your {frequency} Slice of ML [not italic]🍰[/not italic]"
        table.caption = "Made with ❤️  by the team at [bold blue][link=https://notia.ai]Notia[/link][/bold blue]"

        table.add_column("Username 🧑", justify="center")
        table.add_column(
            "Tweet 🐦", justify="center", header_style="bold blue", max_width=100
        )
        table.add_column("Tweet Link 🔗", justify="center")
        table.add_column("Likes ❤️", justify="center", header_style="bold red")

        for tweet in tweets:
            table.add_row(
                self.buildProfileLink(tweet[3]),
                tweet[1],
                self.buildTweetLink(tweet[0]),
                str(tweet[2]),
            )

        self._console.print(table)
