import json
import math
from math import cos, sin
from typing import Dict

from PIL import ImageDraw, Image

from handlers.handler import Handler
from utility.image import get_image_response, get_image_asset


class CSWinMapHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.require_authorization = False

    def on_request(self):
        order = ["anubis", "inferno", "mirage", "vertigo", "overpass", "nuke", "ancient"]

        maps = {}
        for name in order:
            maps[name] = self.query(name, int) or 0

        max_wins = max(1, max(maps.values()))

        sides = len(maps)
        start_angle = -math.pi / 2
        angle = 2 * math.pi / sides

        multiplier = 5
        actual_width, actual_height = 1024, 1024
        width, height = actual_width * multiplier, actual_height * multiplier

        center = width / 2
        radius = width / 3
        offset = 20 * multiplier

        map_size = int(width / 10), int(height / 10)

        image = Image.new("RGBA", (width, height), (128, 128, 128, 30))
        draw = ImageDraw.Draw(image)

        points, lines, images = [], [], []
        for index, name in enumerate(maps):
            percent = maps[name] / max_wins
            cos_x, sin_y = cos(start_angle + index * angle), sin(start_angle + index * angle)

            x, y = center + radius * (cos_x * percent) + (cos_x * offset), center + radius * (sin_y * percent) + (sin_y * offset)
            points.append((x, y))

            lines.append((center + radius * cos_x + (cos_x * offset * 4), center + radius * sin_y + (sin_y * offset * 4), center + (cos_x * offset), center + (sin_y * offset)))

            try:
                map_image = get_image_asset(f"cs2/de_{name}.png").resize(map_size)
                images.append((map_image, int(center + radius * cos_x - (map_size[0] / 2) + (cos_x * map_size[0])), int(center + radius * sin_y - (map_size[1] / 2) + (sin_y * map_size[1]))))
            except:
                pass

        percent = 1 / max_wins

        polygons = []
        for i in range(max_wins + 1):
            polygon_points = []
            for index in range(sides):
                x, y = cos(start_angle + index * angle), sin(start_angle + index * angle)
                polygon_points.append(
                    (center + radius * (x * i * percent) + (x * offset), center + radius * (y * i * percent) + (y * offset)))

            polygons.append(polygon_points)

        draw.polygon(polygons[-1], fill=(255, 255, 255, 0))
        draw.polygon(points, fill=(255, 0, 0, 100))

        for p in range(len(points)):
            draw.line((points[p], points[(p + 1) % len(points)]), fill=(255, 0, 0, 255), width=1 * multiplier)

        for i in range(sides):
            for polygon_points in polygons:
                draw.line([polygon_points[i], polygon_points[(i + 1) % sides]], fill=(255, 255, 255, 255), width=1 * multiplier)

        for line in lines:
            draw.line(line, fill=(255, 255, 255, 255), width=1 * multiplier)

        for map_image in images:
            image.paste(map_image[0], map_image[1:], map_image[0])

        image = image.resize((actual_width, actual_height), Image.LANCZOS)

        return get_image_response([image])
