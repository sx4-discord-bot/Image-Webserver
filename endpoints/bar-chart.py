from math import ceil, log10
from typing import Optional, List, Dict

from PIL import Image, ImageDraw

from handlers.handler import Handler
from utility.colour import as_rgb_tuple
from utility.error import ErrorCode
from utility.image import get_font_asset, get_image_response
from utility.response import BadRequest


class BarGraphHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]
        self.fields += [
            (["max_value"], Optional[int]),
            (["min_value"], Optional[int]),
            (["value_prefix"], Optional[str]),
            (["value_suffix"], Optional[str]),
            (["x_header"], Optional[str]),
            (["y_header"], Optional[str]),
            (["sort"], Optional[str]),
            (["bars"], List[Dict[str, object]])
        ]

        self.require_authorization = False

    def on_request(self):
        max_value = self.body("max_value", int)
        min_value = self.body("min_value", int)
        value_prefix = self.body("value_prefix", str, "")
        value_suffix = self.body("value_suffix", str, "")
        sort = self.body("sort")
        x_header = self.body("x_header")
        y_header = self.body("y_header")

        bars = self.body("bars", list, [])
        if len(bars) == 0:
            raise BadRequest("bars field was empty", ErrorCode.INVALID_FIELD_VALUE)

        if sort and (sort == "asc" or sort == "desc"):
            bars = sorted(bars, key=lambda bar: bar.get("value"), reverse=sort == "desc")

        multiplier = 3
        actual_height, actual_width = 600, 1000
        height, width = actual_height * multiplier, actual_width * multiplier

        excess = int(height * 0.125)
        point_length = int(excess / 7.5)
        graph_width, graph_height = width + excess, height + excess
        y_points = 8
        bar_offset = 25 * multiplier

        image = Image.new("RGBA", (width + excess * 2, height + excess * 2), (128, 128, 128, 30))

        draw = ImageDraw.Draw(image)
        draw.rectangle((excess, excess, graph_width, graph_height), fill=(255, 255, 255, 0),
                       outline=(255, 255, 255, 255), width=1 * multiplier)

        axis_font = get_font_asset("roboto/RobotoMono-Bold.ttf", 10 * multiplier)

        variable = min_value is None or max_value is None
        if variable:
            values = list(map(lambda bar: bar["value"], bars))
            max_value, min_value = max(values), min(values)

        difference = abs(max_value - min_value)
        change = difference / (y_points - (3 if variable else 1))

        if variable:
            max_value += change
            min_value -= change

        difference_graph = abs(max_value - min_value)

        x_change = width - bar_offset * 2 if len(bars) == 1 else (width - (bar_offset * (len(bars) + 1))) / len(bars)

        for index, data in enumerate(bars):
            value = data.get("value")
            if value is None:
                raise BadRequest("value field missing from bars." + str(index), ErrorCode.INVALID_FIELD_VALUE)

            colour = data.get("colour")
            name = data.get("name")

            percent = 0.5 if difference_graph == 0 else max(0, min(1, (max_value - value) / difference_graph))
            x, y = bar_offset * (index + 1) + x_change * index + excess, percent * height + excess

            extra = (x_change * 0.5 if len(bars) == 1 else 0)

            if name:
                font_width, _ = axis_font.getsize(name)
                draw.text((x + extra + x_change / 2 - font_width / 2, graph_height + (excess * 0.1)), name, font=axis_font)

            colour = as_rgb_tuple(colour) if colour is not None else (255, 0, 0)

            draw.rectangle((x, graph_height, x + x_change, y), outline=colour + (255,), fill=colour + (100,), width=2 * multiplier)

        log_value = 0 if change == 0 else log10(abs(change))
        digits = ceil(abs(log_value)) if log_value < 0 else 0

        for index in range(y_points):
            y = (height / (y_points - 1) * index) + excess
            draw.line((excess - point_length, y, graph_width, y), fill=(255, 255, 255, 255), width=1 * multiplier)

            value = max_value - (index * change)

            text = f"{value_prefix}{value:.{digits}f}{value_suffix}"
            font_width, font_height = axis_font.getsize(text)

            draw.text((excess - (excess / 5) - font_width, y - font_height / 1.8), text, font=axis_font)

        if x_header and y_header:
            font = get_font_asset("roboto/RobotoMono-Regular.ttf", excess - (25 * multiplier))
            x_font_width, x_font_height = font.getsize(x_header)
            y_font_width, y_font_height = font.getsize(y_header)

            font_image = Image.new("RGBA", (y_font_width, y_font_height), (128, 128, 128, 30))
            font_draw = ImageDraw.Draw(font_image)
            font_draw.text((0, 0), y_header, font=font)

            font_image = font_image.rotate(270, expand=1)

            image.paste(font_image,
                        (int(width + excess * 2 - y_font_height), int(((height + excess * 2) - y_font_width) / 2)))
            draw.text((((width + excess * 2) - x_font_width) / 2, excess - (excess / 7) - x_font_height), x_header,
                      font=font)

        image = image.resize((actual_width, actual_height), Image.LANCZOS)

        return get_image_response([image])