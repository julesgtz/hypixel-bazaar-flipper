from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, DataTable
from textual.containers import Container
from textual.binding import Binding
from string import ascii_lowercase


class ForgeApp(App):
    DEFAULT_CSS = """#result-box {
    border: solid green;
}"""
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=True),
        Binding("escape", "quit", "Quit", show=True),
    ]

    def __init__(self, items: dict):
        super().__init__()
        self.items = items
        self.allowed_chars = set(ascii_lowercase + "0123456789" + "!")

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(
                placeholder="Enter filter like: (s > 100 or m < 10) and bp > 1000 and sp > 5000",
            )
            with Container():
                yield DataTable()

    def on_mount(self) -> None:
        self.items = sorted(self.items, key=lambda x: x.get("score", 0), reverse=True)
        self.update_table(self.items)

    def update_table(self, items):
        table = self.query_one(DataTable)
        table.clear(columns=True)

        table.add_column("Name")
        table.add_column("Liquidity")
        table.add_column("Marge")
        table.add_column("Buy Price")
        table.add_column("Sell Price")
        table.add_column("Buy 7d")
        table.add_column("Sell 7d")
        table.add_column("Marge %")
        table.add_column("Score")

        for item in items:
            if (
                not int(item.get("liquidity", 0)) > 30000
                or not int(item.get("sell_price", 0)) > 1000
            ):
                continue
            name = item.get("name", "Unknown")
            score = f"{item.get('score', 0):,.2f}".replace(",", " ")
            marge = f"{int(item.get('marge', 0)):,}".replace(",", " ")
            marge_pct = f"{item.get('marge_pct', 0) * 100:.2f} %"
            liquidity = f"{int(item.get('liquidity', 0)):,}".replace(",", " ")
            instabuy = f"{int(item.get('nbr_instabuy', 0)):,}".replace(",", " ")
            instasell = f"{int(item.get('nbr_instasell', 0)):,}".replace(",", " ")
            buy_price = f"{int(item.get('buy_price', 0)):,}".replace(",", " ")
            sell_price = f"{int(item.get('sell_price', 0)):,}".replace(",", " ")

            table.add_row(
                name,
                liquidity,
                marge,
                buy_price,
                sell_price,
                instabuy,
                instasell,
                marge_pct,
                score,
            )

    def filter_items(self, query):
        if not query.strip():
            return self.items

        _query = (
            query.replace("(", " ( ")
            .replace(")", " ) ")
            .replace(">", " > ")
            .replace("<", " < ")
        ).lower()
        _temp_query = list()
        idx = last_idx = 0
        for char in query.replace(" ", ""):
            if char not in self.allowed_chars or idx == len(
                query
            ):  # parenthese ou operateur
                _temp_query.append(_query[last_idx:idx])
                last_idx = idx
            idx += 1
        _dict_replacer = {
            "s": "score",
            "bp": "buy_price",
            "sp": "sell_price",
            "p": "profit",
            "m": "marge",
            "mp": "marge_pct",
            "l": "liquidity",
        }

        query_list = [_dict_replacer.get(q, q) for q in _query.split()]

        allowed_words = {
            "profit",
            "score",
            "buy_price",
            "sell_price",
            "marge",
            "marge_pct",
            "liquidity",
            "and",
            "or",
            "not",
        }
        allowed_chars = set("()0123456789<>=!")
        for word in query_list:
            if word not in allowed_words:
                if not all(char.lower() in allowed_chars for char in word):
                    return []

        query = " ".join(query_list)

        results = []
        for item in self.items:
            context = {
                "profit": item.get("profit", 0),
                "score": item.get("score", 0),
                "buy_price": item.get("buy_price", 0),
                "sell_price": item.get("sell_price", 0),
                "marge": item.get("marge", 0),
                "marge_pct": item.get("marge_pct", 0) * 100,
                "liquidity": item.get("liquidity", 0),
            }
            try:
                if eval(query, {}, context):
                    results.append(item)
            except Exception:
                continue
        return results

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value
        filtered_items = self.filter_items(query)
        self.update_table(filtered_items)

    def action_quit(self) -> None:
        self.app.exit()


if __name__ == "__main__":
    app = ForgeApp()
    app.run()
