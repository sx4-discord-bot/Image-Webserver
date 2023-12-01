import json
import math
from math import cos, sin
from typing import Dict, List, Optional

from PIL import ImageDraw, Image

from handlers.handler import Handler
from utility.colour import as_rgb_tuple
from utility.error import ErrorCode
from utility.image import get_image_response, get_image_asset, get_image, get_font_asset
from utility.response import BadRequest


class RadarChartHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]
        self.fields += [
            (["data"], List[Dict[str, object]]),
            (["colours"], Optional[List[int]]),
            (["legends"], Optional[List[str]]),
            (["sort_colours"], Optional[bool]),
            (["fill"], Optional[bool])
        ]

        self.require_authorization = False

    def on_request(self):
        data = self.body("data", list)

        sides = len(data)
        if sides < 5:
            raise BadRequest("data field cannot have less than 5 values", ErrorCode.INVALID_FIELD_VALUE)

        max_value, max_length = 1, 0
        for index, point in enumerate(data):
            values = point.get("values")
            if not isinstance(values, list):
                raise BadRequest(f"data.{index}.values is not a list", ErrorCode.INVALID_FIELD_VALUE)

            max_length = max(max_length, len(values))
            max_value = max(max_value, max(values))

        colours = self.body("colours", list, [])
        legends = self.body("legends", list, [])
        sort_colours = self.body("sort_colours", bool, True)
        fill = self.body("fill", bool, True)

        start_angle = -math.pi / 2
        angle = 2 * math.pi / sides

        multiplier = 3
        actual_width, actual_height = 1024, 1024
        width, height = actual_width * multiplier, actual_height * multiplier

        center = width / 2
        radius = width / 3
        offset = 20 * multiplier

        icon_size = int(width / 10), int(height / 10)

        image = Image.new("RGBA", (width, height), (128, 128, 128, 30))
        draw = ImageDraw.Draw(image)
        font = get_font_asset("roboto/RobotoMono-Bold.ttf", 15 * multiplier)

        percent = 1 / max_value

        polygons = []
        for i in range(max_value + 1):
            polygon_points = []
            for index in range(sides):
                x, y = cos(start_angle + index * angle), sin(start_angle + index * angle)
                polygon_points.append(
                    (center + radius * (x * i * percent) + (x * offset),
                     center + radius * (y * i * percent) + (y * offset)))

            polygons.append(polygon_points)

        draw.polygon(polygons[-1], fill=(255, 255, 255, 0))

        for i in range(sides):
            for polygon_points in polygons:
                draw.line([polygon_points[i], polygon_points[(i + 1) % sides]], fill=(255, 255, 255, 255),
                          width=1 * multiplier)

        range_length = range(max_length)
        if sort_colours:
            positions = [[] for _ in range(max_length)]
            for point in data:
                values = point.get("values")
                sorted_values = sorted(values, reverse=True)

                for i in range_length:
                    positions[i].append(sorted_values.index(values[i]))

            mean = [sum(x) / len(x) for x in positions]
            colours = sorted(colours, key=lambda c: (0.2126 * ((c >> 16) & 0xFF) + 0.7152 * ((c >> 8) & 0xFF) + 0.0722 * (c & 0xFF)))

            def check_index(other, v):
                other_index = other.index(v)
                return 0 if len(mean) <= other_index else mean[other_index]

            colours = sorted(colours, key=lambda x: check_index(colours, x))
            range_length = sorted(range_length, key=lambda x: check_index(range_length, x))

        for i in range_length:
            polygon_image = Image.new("RGBA", image.size, 0)
            polygon_draw = ImageDraw.Draw(polygon_image)

            polygon, lines = [], []
            for index, point in enumerate(data):
                values = point.get("values")
                value = values[i]

                percent = value / max_value
                cos_x, sin_y = cos(start_angle + index * angle), sin(start_angle + index * angle)

                x, y = center + radius * (cos_x * percent) + (cos_x * offset), center + radius * (sin_y * percent) + (sin_y * offset)
                polygon.append((x, y))

                if i != range_length[0]:
                    continue

                icon_url = point.get("icon")
                text = point.get("text")
                extra = 4 if icon_url is not None else 2 if text is not None else 1

                line = (center + radius * cos_x + (cos_x * offset * extra), center + radius * sin_y + (sin_y * offset * extra), center + (cos_x * offset), center + (sin_y * offset))
                draw.line(line, fill=(255, 255, 255, 255), width=1 * multiplier)

                if icon_url is not None:
                    try:
                        icon = get_image_asset(icon_url)
                    except:
                        icon = get_image(icon_url, f"data.{index}.icon", "field")

                    icon = icon.resize(icon_size)

                    image.paste(icon, (int(center + radius * cos_x - (icon_size[0] / 2) + (cos_x * icon_size[0])),
                                       int(center + radius * sin_y - (icon_size[1] / 2) + (sin_y * icon_size[1]))), icon)
                elif text is not None:
                    text_size = font.getsize(text)

                    draw.text((center + radius * cos_x + (cos_x * offset * 2.2) - (text_size[0] / 2) + (cos_x * text_size[0] * 0.7), center + radius * sin_y + (sin_y * offset * 2.2) - (text_size[1] / 2) + (sin_y * text_size[1] * 0.7)), text, font=font)

            colour = colours[i] if len(colours) > i else None
            colour = (255, 0, 0) if colour is None else as_rgb_tuple(colour)

            if fill:
                polygon_draw.polygon(polygon, fill=colour + (100,))

            for p in range(len(polygon)):
                polygon_draw.line((polygon[p], polygon[(p + 1) % len(polygon)]), fill=colour + (255,), width=2 * multiplier)

            image = Image.alpha_composite(image, polygon_image)

        draw = ImageDraw.Draw(image)

        legend_width = 15 * multiplier
        rectangle_size = 15 * multiplier
        for i in range(max_length):
            if len(legends) <= i:
                continue

            name = legends[i]
            colour = colours[i] if len(colours) > i else None
            colour = (255, 0, 0) if colour is None else as_rgb_tuple(colour)

            draw.rectangle((legend_width, height - rectangle_size * 2, legend_width + rectangle_size, height - rectangle_size), fill=colour + (255,))
            legend_width += rectangle_size + 5 * multiplier

            draw.text((legend_width, height - rectangle_size * 2.2), name, font=font)
            legend_width += font.getsize(name)[0] + rectangle_size * 1.2

        image = image.resize((actual_width, actual_height), Image.LANCZOS)

        return get_image_response([image])
