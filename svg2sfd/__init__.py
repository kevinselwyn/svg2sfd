#!/usr/bin/python
"""svg2png"""

import math
import os
import pwd
import re
import time
import xml.etree.ElementTree as ET
from datetime import date

class SVG2SFD(object):
    """SVG2PNG class"""

    def __init__(self, filename='', opts=None):
        """Constructor function"""

        svg = self.load_svg(filename)
        self.data = self.parse_svg(svg, opts)

    def load_svg(self, filename=''):
        """Load SVG"""

        try:
            tree = ET.parse(filename)
        except IOError:
            return None

        return tree.getroot()

    def save_sfd(self, filename=''):
        """Save SFD"""

        with open(filename, 'w') as sfd:
            sfd.write(self.data)

    def parse_path(self, path=''):
        """Parse SVG <path>"""

        output = []

        mode = ''
        last_mode = ''
        lengths = {
            'm': 2,
            'l': 2,
            'h': 1,
            'v': 1,
            'c': 6,
            's': 4,
            'z': 1
        }
        i = 0

        path = re.sub('([a-zA-Z])', ' \g<1> ', path)
        path = re.sub('([0-9])-([0-9])', '\g<1> -\g<2>', path)
        path = re.sub('[ \tZ]+', ' ', path).strip()
        params = re.split('[ \t\n,]', path)

        while i < len(params):
            param = params[i]
            ctrl = True

            mode = param.lower()

            if not mode in lengths:
                mode = 'l'
                ctrl = False

            length = lengths[mode]

            args = params[i + (1 if ctrl else 0):i + length + (1 if ctrl else 0)]
            i += length + (1 if ctrl else 0)

            if mode in ['h', 'v']:
                x = float(output[len(output) - 1][0])
                y = float(output[len(output) - 1][1])

                if mode == 'h':
                    args = [
                        args[0],
                        y
                    ]
                else:
                    args = [
                        x,
                        args[0]
                    ]

                mode = 'l'

            args.extend([mode, '1'])

            last_mode = mode
            output.append(args)

        return output

    def parse_polygon(self, points=''):
        """Parse SVG <polygon>"""

        output = []

        path = re.sub('[ \tZ]+', ' ', points).strip()
        params = re.split('[ \t\n,]', path)

        for i in range(0, len(params), 2):
            output.append([
                params[i], params[i + 1], 'l', '1'
            ])

        output[0][2] = 'm'

        return output

    def parse_circle(self, cx='', cy='', r=''):
        """Parse SVG <circle>"""

        cx = float(cx)
        cy = float(cy)
        r = float(r)
        ctrl = float((4 * (math.sqrt(2) - 1)) / 3) * r

        output = [
            [cx - r, cy, 'm', '1'],
            [cx - r, cy - ctrl, cx - ctrl, cy - r, cx, cy - r, 'c', '1'],
            [cx + ctrl, cy - r, cx + r, cy - ctrl, cx + r, cy, 'c', '1'],
            [cx + r, cy + ctrl, cx + ctrl, cy + r, cx, cy + r, 'c', '1'],
            [cx - ctrl, cy + r, cx - r, cy + ctrl, cx - r, cy, 'c', '1']
        ]

        return output

    def parse_ellipse(self, cx='', cy='', rx='', ry=''):
        """Parse SVG <ellipse>"""

        cx = float(cx)
        cy = float(cy)
        rx = float(rx)
        ry = float(ry)
        ctrl_x = float((4 * (math.sqrt(2) - 1)) / 3) * rx
        ctrl_y = float((4 * (math.sqrt(2) - 1)) / 3) * ry

        output = [
            [cx - rx, cy, 'm', '1'],
            [cx - rx, cy - ctrl_y, cx - ctrl_x, cy - ry, cx, cy - ry, 'c', '1'],
            [cx + ctrl_x, cy - ry, cx + rx, cy - ctrl_y, cx + rx, cy, 'c', '1'],
            [cx + rx, cy + ctrl_y, cx + ctrl_x, cy + ry, cx, cy + ry, 'c', '1'],
            [cx - ctrl_x, cy + ry, cx - rx, cy + ctrl_y, cx - rx, cy, 'c', '1']
        ]

        return output

    def parse_rect(self, x='', y='', width='', height=''):
        """Parse SVG <rect>"""

        x = float(x)
        y = float(y)
        width = float(width)
        height = float(height)

        output = [
            [x, y, 'm', '1'],
            [x + width, y, 'l', '1'],
            [x + width, y + height, 'l', '1'],
            [x, y + height, 'l', '1']
        ]

        return output

    def parse_clean(self, output=None, grid_width=0, grid_height=0):
        """Cleans up parsed output"""

        x_min = float('inf')
        x_max = 0
        x_offset = 0
        y_min = float('inf')
        y_max = 0
        y_offset = 0

        cell_width = 1000
        cell_height = cell_width

        for i, row in enumerate(output):
            for j in range(0, len(row) - 2):
                if j % 2 == 0:
                    x_min = min(x_min, float(row[j]))
                    x_max = max(x_max, float(row[j]))
                else:
                    y_min = min(y_min, float(row[j]))
                    y_max = max(y_max, float(row[j]))

        for grid_y in range(0, grid_height * cell_height, cell_height):
            for grid_x in range(0, grid_width * cell_width, cell_width):
                if (x_min >= grid_x and x_max < grid_x + cell_width and
                        y_min >= grid_y and y_max < grid_y + cell_height):
                    x_offset = grid_x
                    y_offset = grid_y

        if not output:
            output = []

        for i, row in enumerate(output):
            for j in range(len(row) - 2):
                output[i][j] = float(output[i][j])

                if j % 2 == 1:
                    output[i][j] = 800 - (output[i][j] - y_offset)
                else:
                    output[i][j] = output[i][j] - x_offset

                output[i][j] = ('%4.9f' % (output[i][j])).rstrip('0').rstrip('.')

            output[i] = ' '.join(output[i])

        origin = output[0]
        origin = origin[:-3] + 'l 1'
        output.append(origin)

        output[0] = (output[0], '')

        for i in range(1, len(output)):
            output[i] = (' %s' % (output[i]), '')

        return output

    def parse_svg(self, svg=None, opts=None):
        """Parse SVG"""

        now = time.time()
        output = []
        data = []
        chars = []

        cell_width = 1000
        cell_height = cell_width
        svg_width = int(re.sub('[^0-9]', '', svg.attrib['width']))
        svg_height = int(re.sub('[^0-9]', '', svg.attrib['height']))
        grid_width = svg_width / cell_width
        grid_height = svg_height / cell_height

        char_additional = 0
        startchar_index = 0

        weights = [
            'Thin', 
            'Extra Light',
            'Light',
            'Regular',
            'Medium',
            'Semi Bold',
            'Bold',
            'Extra Bold',
            'Black'
        ]

        for group in svg:
            tag = re.sub('{.*}', '', group.tag)

            if tag == 'g':
                chars.append(group)

        if not opts:
            opts = {}

        name = 'Font'
        family = 'Family'
        right = ''
        weight = ''
        ttfweight = '400'
        version = ''
        encoding = 'ISO8859-1'

        if 'name' in opts and opts['name']:
            name = opts['name']

        if 'family' in opts and opts['family']:
            family = opts['family']

        if 'copyright' in opts and opts['copyright']:
            right = opts['copyright']
        else:
            year = date.today().year
            user = pwd.getpwuid(os.getuid())[4]
            right = 'Copyright (c) %d %s' % (year, user)

        if 'weight' in opts and opts['weight']:
            weight = opts['weight']

            if weight.isdigit():
                ttfweight = weight
                weight = weights[(int(weight) / 100) - 1]
            
        else:
            weight = 'Regular'

        if 'version' in opts and opts['version']:
            version = opts['version']
        else:
            version = '1.0.1'

        output.extend([
            ('SplineFontDB', '3.0'),
            ('FontName', name),
            ('FullName', name),
            ('FamilyName', family),
            ('Copyright', right),
            ('Weight', weight),
            ('TTFWeight', ttfweight),
            ('Version', version),
            ('Ascent', '%d' % (cell_height * 0.8)),
            ('Descent', '%d' % (cell_height * 0.2)),
            ('CreationTime', '%d' % (now)),
            ('ModificationTime', '%d' % (now)),
            ('Encoding', encoding),
            ('LayerCount', '2'),
            ('Layer', '0 0 "Back" 1'),
            ('Layer', '1 0 "Fore" 0'),
            ('AntiAlias', '1'),
            ('BeginChars', '%d %d\n' % (256, len(chars))),
        ])

        for i in range(0, len(chars)):
            char = chars[i]
            char_index = 0
            char_code = 0
            startchar = ''

            if 'id' in char.attrib:
                code = re.findall('(U\+|0x)([a-zA-Z0-9]+)', char.attrib['id'])

                if len(code) and len(code[0]):
                    startchar = char.attrib['id']
                    char_additional += 1
                    char_index = char_additional + 255
                    char_code = int(code[0][1], 16)
                else:
                    startchar = char.attrib['id'][:1]
                    char_index = ord(startchar)
                    char_code = char_index
            else:
                startchar_index += 1
                startchar = chr(0x41) if i == 0 else chr(0x41 + startchar_index)
                char_index = ord(startchar)
                char_code = char_index

            output.extend([
                ('StartChar', startchar),
                ('Encoding', '%d %d %d' % (char_index, char_code, i)),
                ('Width', str(cell_width)),
                ('VWidth', '0'),
                ('Flags', 'H'),
                ('LayerCount', '2'),
                ('Fore', ''),
                ('SplineSet', '')
            ])

            for el in char:
                data = []
                tag = re.sub('{.*}', '', el.tag)

                if tag == 'path':
                    for d in re.split('[zZ]', el.attrib['d']):
                        d = d.strip()

                        if len(d) == 0:
                            continue

                        data = self.parse_path(d)
                        output.extend(self.parse_clean(data, grid_width, grid_height))
                else:
                    if tag == 'polygon':
                        data = self.parse_polygon(el.attrib['points'])
                    if tag == 'circle':
                        data = self.parse_circle(el.attrib['cx'], el.attrib['cy'], el.attrib['r'])
                    elif tag == 'ellipse':
                        data = self.parse_ellipse(el.attrib['cx'], el.attrib['cy'], el.attrib['rx'], el.attrib['ry'])
                    elif tag == 'rect':
                        data = self.parse_rect(el.attrib['x'], el.attrib['y'], el.attrib['width'], el.attrib['height'])

                    if len(data):
                        output.extend(self.parse_clean(data, grid_width, grid_height))

            output.extend([
                ('EndSplineSet', ''),
                ('EndChar', '')
            ])

            if i + 1 < len(chars):
                output.extend([
                    ('', '')
                ])

        output.extend([
            ('EndChars', ''),
            ('EndSplineFont', '')
        ])

        for i in range(0, len(output)):
            output[i] = re.sub(': $', '', ': '.join(output[i]))

        return '\n'.join(output)
