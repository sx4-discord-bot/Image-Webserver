import numbers
from functools import reduce
from math import ceil, log10, floor
from typing import Optional, List

from PIL import Image, ImageDraw, ImageOps, ImageFont

from handlers.handler import Handler
from utility.colour import as_rgb_tuple
from utility.error import ErrorCode
from utility.image import get_image_response, get_font_asset
from utility.response import BadRequest


class LineGraphHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]
        self.require_authorization = False

    def on_request(self):
        data = self.body("data", list)

        max_length = 0
        for index, point in enumerate(data):
            name = point.get("name")
            if name is None:
                raise BadRequest(f"data.{index}.name does not exist", ErrorCode.INVALID_FIELD_VALUE)

            if not isinstance(name, str):
                raise BadRequest(f"data.{index}.name is not a string", ErrorCode.INVALID_FIELD_VALUE)

            values = point.get("value")
            if values is None:
                raise BadRequest(f"data.{index}.value does not exist", ErrorCode.INVALID_FIELD_VALUE)

            if isinstance(values, numbers.Number):
                values = [values]
                point["value"] = values

            if not isinstance(values, list):
                raise BadRequest(f"data.{index}.value is not a list", ErrorCode.INVALID_FIELD_VALUE)

            max_length = max(max_length, len(values))

        x_header = self.query("x_header") or self.body("x_header")
        y_header = self.query("y_header") or self.body("y_header")
        colours = self.body("colours", list, [])
        legends = self.body("legends", list, [])
        key_points = self.body("key_points", list, [])
        max_value = self.body("max_value", int)
        min_value = self.body("min_value", int)
        value_prefix = self.body("value_prefix", str, "")
        value_suffix = self.body("value_suffix", str, "")
        sort_colours = self.body("sort_colours", bool, True)
        y_points = self.body("steps", int, 7) + 1
        if y_points < 2:
            raise BadRequest(f"steps needs to be a value more than 0", ErrorCode.INVALID_FIELD_VALUE)

        multiplier = 3
        actual_height, actual_width = 600, 1000
        height, width = actual_height * multiplier, actual_width * multiplier

        excess = int(height * 0.125)
        default_point_length = int(excess / 7.5)
        graph_width, graph_height = width + excess, height + excess

        image = Image.new("RGBA", (width + excess * 2, height + excess * 2), (128, 128, 128, 30))

        draw = ImageDraw.Draw(image)
        draw.rectangle((excess, excess, graph_width, graph_height), fill=(255, 255, 255, 0), outline=(255, 255, 255, 255), width=1 * multiplier)

        axis_font = get_font_asset("roboto/RobotoMono-Bold.ttf", 10 * multiplier)

        variable = min_value is None or max_value is None
        if variable:
            values = [x for x in reduce(lambda a, b: a + b["value"], data, []) if x is not None]
            max_value, min_value = max(values), min(values)
            difference = abs(max_value - min_value)
            if difference == 0:
                change = 1 if max_value == 0 else 10 ** ceil(log10(max_value) - 1)
                min_value -= change
                max_value += change
            else:
                change = difference / 7
                power = 10 ** ceil(log10(change) - 1)
                change = ceil(change / power + 1) * power

                min_value = change * floor(min_value / change)
                max_value = change * ceil((max_value + 1) / change)

            difference_graph = abs(max_value - min_value)
            y_points = round(difference_graph / change) + 1
        else:
            difference = abs(max_value - min_value)
            change = difference / (y_points - 1)
            difference_graph = difference

        x_change = width if len(data) == 1 else width / (len(data) - 1)

        max_text_length = max([axis_font.getsize(x["name"])[0] for x in data])
        points_per_text = ceil(max_text_length / (width / len(data) * 0.8))

        range_length = range(max_length)
        if sort_colours:
            positions = [[] for _ in range(max_length)]
            for point in data:
                values = point.get("value")
                sorted_values = sorted(values, reverse=True)

                for i in range_length:
                    value = values[i]
                    if value is None:
                        continue

                    positions[i].append(sorted_values.index(value))

            mean = [sum(x) / len(x) for x in positions]
            colours = sorted(colours, key=lambda c: (0.2126 * ((c >> 16) & 0xFF) + 0.7152 * ((c >> 8) & 0xFF) + 0.0722 * (c & 0xFF)))

            def check_index(d, x):
                d_index = d.index(x)
                return 0 if len(mean) <= d_index else mean[d_index]

            colours = sorted(colours, key=lambda x: check_index(colours, x))
            range_length = sorted(range_length, key=lambda x: check_index(range_length, x))

        for i in range_length:
            polygon_image = Image.new("RGBA", image.size, 0)
            polygon_draw = ImageDraw.Draw(polygon_image)

            polygon = [(excess, height + excess)]
            for index, point in enumerate(data):
                name = point.get("name")

                x = x_change * index + excess
                if i == 0:
                    extra = (x_change * 0.5 if len(data) == 1 else 0)

                    point_length = default_point_length
                    if index % points_per_text == 0:
                        font_width, _ = axis_font.getsize(name)
                        draw.text((x + extra - font_width / 2, graph_height + (excess * 0.2)), name, font=axis_font)
                    else:
                        point_length /= 2

                    draw.line((x + extra, graph_height, x + extra, graph_height + point_length), fill=(255, 255, 255, 255),
                              width=1 * multiplier)

                values = point.get("value")
                value = values[i]
                if value is None:
                    polygon.append((polygon[-1][0], graph_height))
                    break

                percent = 0.5 if difference_graph == 0 else max(0, min(1, (max_value - value) / difference_graph))

                y = percent * height + excess
                polygon.append((x, y))
                if len(data) == 1:
                    polygon.append((x_change + excess, y))
            else:
                polygon.append((graph_width, graph_height))

            colour = colours[i] if len(colours) > i else None
            colour = (255, 0, 0) if colour is None else as_rgb_tuple(colour)

            polygon_draw.polygon(polygon, fill=colour + (100,))

            line_points = polygon[1:-1]
            for p in range(len(line_points) - 1):
                polygon_draw.line((line_points[p], line_points[p + 1]), fill=colour + (255,), width=2 * multiplier)

            image = Image.alpha_composite(image, polygon_image)

        draw = ImageDraw.Draw(image)

        legend_width = excess
        rectangle_size = 10 * multiplier

        for i in range(max_length):
            if len(legends) <= i:
                continue

            name = legends[i]

            colour = colours[i] if len(colours) > i else None
            colour = (255, 0, 0) if colour is None else as_rgb_tuple(colour)

            excess_center = graph_height + excess - (excess / 3)
            draw.rectangle((legend_width, excess_center - (rectangle_size / 2), legend_width + rectangle_size,
                            excess_center + (rectangle_size / 2)), fill=colour + (255,))

            legend_width += rectangle_size + 5 * multiplier

            draw.text((legend_width, excess_center - rectangle_size / 1.4), name, font=axis_font)

            legend_width += axis_font.getsize(name)[0] + 15 * multiplier

        log_value = 0 if change == 0 else log10(abs(change))
        digits = ceil(abs(log_value)) if log_value < 0 else 0

        for index in range(y_points):
            y = (height / (y_points - 1) * index) + excess
            draw.line((excess - default_point_length, y, graph_width, y), fill=(255, 255, 255, 255), width=1 * multiplier)

            value = max_value - (index * change)

            text = f"{value_prefix}{value:.{digits}f}{value_suffix}"
            font_width, font_height = axis_font.getsize(text)

            draw.text((excess - (excess / 5) - font_width, y - font_height / 1.8), text, font=axis_font)

        for key_point in key_points:
            value = key_point.get("value")
            if value is None:
                continue

            if value <= min_value or value >= max_value:
                continue

            percent = (max_value - value) / difference_graph
            y = percent * height + excess

            colour = key_point.get("colour")

            draw.line((excess, y, graph_width, y), fill=(as_rgb_tuple(colour) if colour is not None else (255, 0, 0)) + (255,), width=2 * multiplier)

        draw.rectangle((excess, excess, graph_width, graph_height), outline=(255, 255, 255, 255))

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
