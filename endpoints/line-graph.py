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

        self.methods = ["GET", "POST"]
        self.require_authorization = False

    def on_request(self):
        x_header = self.query("x_header")
        y_header = self.query("y_header")

        points, colours, key_points = {}, [], []
        if self.request.method == "GET":
            for query in self.request.args:
                if query == "x_header" or query == "y_header":
                    continue

                points[query] = [self.query(query, int)]
        else:
            data = self.body("data", dict)
            for key in data:
                value = data[key]
                if isinstance(value, list):
                    points[key] = value
                elif isinstance(value, int):
                    points[key] = [value]
                else:
                    raise BadRequest("values need to be of type int or list", ErrorCode.INVALID_FIELD_VALUE)

            colours = self.body("colours", list, [])
            key_points = self.body("key_points", list, [])

        values = list(filter(lambda a: a, reduce(lambda a, b: a + b, points.values())))

        multiplier = 3
        actual_height, actual_width = 600, 1000
        height, width = actual_height * multiplier, actual_width * multiplier

        excess = int(height * 0.125)
        default_point_length = int(excess / 7.5)
        graph_width, graph_height = width + excess, height + excess
        y_points = 8

        image = Image.new("RGBA", (width + excess * 2, height + excess * 2), (128, 128, 128, 30))

        draw = ImageDraw.Draw(image)
        draw.rectangle((excess, excess, graph_width, graph_height), fill=(255, 255, 255, 0), outline=(255, 255, 255, 255), width=1 * multiplier)

        axis_font = get_font_asset("roboto/RobotoMono-Bold.ttf", 10 * multiplier)

        max_value, min_value = max(values), min(values)
        difference = abs(max_value - min_value)

        change = difference / (y_points - 3)
        max_value += change
        min_value -= change
        difference_graph = abs(max_value - min_value)

        x_change = width if len(points) == 1 else width / (len(points) - 1)

        max_length = max(map(lambda n: axis_font.getsize(n)[0], points.keys()))
        points_per_text = ceil(max_length / (width / len(points) * 0.8))

        for i in range(max(map(len, points.values()))):
            polygon_image = Image.new("RGBA", image.size, 0)
            polygon_draw = ImageDraw.Draw(polygon_image)

            polygon = [(excess, height + excess)]
            for index, name in enumerate(points):
                x = x_change * index + excess
                if i == 0:
                    extra = (x_change * 0.5 if len(points) == 1 else 0)

                    point_length = default_point_length
                    if index % points_per_text == 0:
                        font_width, _ = axis_font.getsize(name)
                        draw.text((x + extra - font_width / 2, graph_height + (excess * 0.2)), name, font=axis_font)
                    else:
                        point_length /= 2

                    draw.line((x + extra, graph_height, x + extra, graph_height + point_length), fill=(255, 255, 255, 255),
                              width=1 * multiplier)

                value = points[name][i]
                if not value:
                    polygon.append((polygon[-1][0], graph_height))
                    break

                percent = 0.5 if difference_graph == 0 else (max_value - value) / difference_graph

                y = percent * height + excess
                polygon.append((x, y))
                if len(points) == 1:
                    polygon.append((x_change + excess, y))
            else:
                polygon.append((graph_width, graph_height))

            colour_data = colours[i] if len(colours) > i else {"colour": 16711680}

            colour = as_rgb_tuple(colour_data.get("colour"))
            polygon_draw.polygon(polygon, fill=colour + (100,))

            line_points = polygon[1:-1]
            for p in range(len(line_points) - 1):
                polygon_draw.line((line_points[p], line_points[p + 1]), fill=colour + (255,), width=2 * multiplier)

            image = Image.alpha_composite(image, polygon_image)

        draw = ImageDraw.Draw(image)

        legend_width = excess
        rectangle_size = 10 * multiplier

        for colour_data in colours:
            colour = colour_data.get("colour")
            if colour is None:
                continue

            name = colour_data.get("name")
            if name:
                excess_center = graph_height + excess - (excess / 3)
                draw.rectangle((legend_width, excess_center - (rectangle_size / 2), legend_width + rectangle_size,
                                excess_center + (rectangle_size / 2)), fill=as_rgb_tuple(colour) + (255,))

                legend_width += rectangle_size + 5 * multiplier

                draw.text((legend_width, excess_center - rectangle_size / 1.4), name, font=axis_font)

                legend_width += axis_font.getsize(name)[0] + 15 * multiplier

        log_value = 0 if change == 0 else log10(abs(change))
        digits = ceil(abs(log_value)) if log_value < 0 else 0

        for index in range(y_points):
            y = (height / (y_points - 1) * index) + excess
            draw.line((excess - default_point_length, y, graph_width, y), fill=(255, 255, 255, 255), width=1 * multiplier)

            value = max_value - (index * change)

            text = f"{value:.{digits}f}"
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
