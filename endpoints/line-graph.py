from math import ceil, log10, floor
from typing import Optional

from PIL import Image, ImageDraw, ImageOps

from handlers.handler import Handler
from utility.error import ErrorCode
from utility.image import get_image_response, get_font_asset
from utility.response import BadRequest


class LineGraphHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.require_authorization = False

    def on_request(self):
        x_header, y_header = None, None

        points = {}
        for query in self.request.args:
            if query == "x_header":
                x_header = self.query(query)
                continue
            elif query == "y_header":
                y_header = self.query(query)
                continue

            points[query] = self.query(query, int)

        height, width = 600, 1000
        excess = 75
        default_point_length = 10
        graph_width, graph_height = width + excess, height + excess
        y_points = 8

        image = Image.new("RGBA", (width + excess * 2, height + excess * 2), (128, 128, 128, 30))

        draw = ImageDraw.Draw(image)
        draw.rectangle((excess, excess, graph_width, graph_height), fill=(255, 255, 255, 0))

        max_value, min_value = max(points.values()), min(points.values())
        difference = abs(max_value - min_value)

        change = difference / (y_points - 3)
        max_value += change
        min_value -= change
        difference_graph = abs(max_value - min_value)

        x_change = width if len(points) == 1 else width / (len(points) - 1)

        max_length = max(map(lambda n: draw.textsize(n)[0], points.keys()))
        points_per_text = ceil(max_length / (width / len(points) * 0.8))

        polygon = [(excess, height + excess)]
        for index, name in enumerate(points):
            value = points[name]
            percent = 0.5 if difference_graph == 0 else (max_value - value) / difference_graph

            x, y = x_change * index + excess, percent * height + excess
            polygon.append((x, y))
            if len(points) == 1:
                polygon.append((x_change + excess, percent * height + excess))

            extra = (x_change * percent if len(points) == 1 else 0)

            point_length = default_point_length
            if index % points_per_text == 0:
                font_width, _ = draw.textsize(name)
                draw.text((x + extra - font_width / 2 + 1, graph_height + 15), name)
            else:
                point_length /= 2

            draw.line((x + extra, graph_height, x + extra, graph_height + point_length), fill=(255, 255, 255, 255), width=1)

        polygon.append((graph_width, graph_height))
        draw.polygon(polygon, fill=(255, 0, 0, 100), outline=(255, 0, 0, 255))

        log_value = log10(abs(change))
        digits = ceil(abs(log_value)) if log_value < 0 else 0

        for index in range(y_points):
            y = (height / (y_points - 1) * index) + excess
            draw.line((excess - 10, y, graph_width, y), fill=(255, 255, 255, 255), width=1)

            value = max_value - (index * change)

            text = f"{value:.{digits}f}"
            font_width, _ = draw.textsize(text)

            draw.text((excess - (excess / 5) - font_width, y - 5), text)

        draw.rectangle((excess, excess, graph_width, graph_height), outline=(255, 255, 255, 255))

        if x_header and y_header:
            font = get_font_asset("whitney/whitney-book.otf", excess - 25)
            x_font_width, x_font_height = font.getsize(x_header)
            y_font_width, y_font_height = font.getsize(y_header)

            font_image = Image.new("RGBA", (y_font_width, y_font_height), (128, 128, 128, 30))
            font_draw = ImageDraw.Draw(font_image)
            font_draw.text((0, 0), y_header, font=font)

            font_image = font_image.rotate(270, expand=1)

            image.paste(font_image, (int(width + excess * 2 - y_font_height), int(((height + excess * 2) - y_font_width) / 2)))
            draw.text((((width + excess * 2) - x_font_width) / 2, excess - (excess / 7) - x_font_height), x_header, font=font)

        return get_image_response([image])
