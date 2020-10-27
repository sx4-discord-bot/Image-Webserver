from typing import Type, Tuple, Any, List

from handlers.handler import Handler


class EndpointsHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

    def format_queries(self, queries: List[Tuple[List[str], Type[Any]]]) -> str:
        builder = []
        for i, (names, t) in enumerate(queries):
            builder.append(f"{' or '.join(names)}: <span style=\"color:red;\">")
            if hasattr(t, "__args__"):
                args = t.__args__
                if len(args) == 2 and args[1] is type(None):
                    builder.append(f"{args[0].__name__}?")
            else:
                builder.append(t.__name__)

            builder.append("</span>")

            if i != len(queries) - 1:
                builder.append(", ")

        return "".join(builder)

    def __call__(self):
        builder = []
        for endpoint in self.app.endpoints:
            builder.append("<header><h1><u>")
            builder.append(endpoint.name)
            builder.append("</u></h1></header>")
            builder.append("Methods: ")
            builder.append("<span style=\"color:purple;\">")
            builder.append(", ".join(endpoint.methods))
            builder.append("</span>")
            builder.append("<br/>")
            builder.append("Aliases: ")
            builder.append("None" if len(endpoint.aliases) == 0 else ", ".join(endpoint.aliases))
            builder.append("<br/>")
            builder.append("Queries: ")
            builder.append(self.format_queries(endpoint.queries))

        return "".join(builder)
