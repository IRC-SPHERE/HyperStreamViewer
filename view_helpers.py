# The MIT License (MIT)
# Copyright (c) 2014-2017 University of Bristol
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
from flask import Response, make_response
from jinja2 import Undefined
import itertools
from pprint import PrettyPrinter
from werkzeug.routing import BaseConverter
from datetime import datetime
import simplejson as json
from StringIO import StringIO
import csv
import xml.etree.ElementTree as ET
import ciso8601

from hyperstream.utils import UTC, MIN_DATE, utcnow, MAX_DATE


pp = PrettyPrinter(indent=4)


def custom_sort(iterable):
    if iterable is None or isinstance(iterable, Undefined):
        return iterable

    # Do custom sorting of iterable here
    iterable = sorted(iterable, key=lambda x: len(x.split(".")), reverse=False)
    return iterable


def custom_format(value, template):
    if isinstance(value, (list, tuple)):
        return ''.join(map(lambda x: template.format(x), value))
    if isinstance(value, dict):
        return template.format('<pre>' + pp.pformat(value) + '</pre>')
    return template.format(value)


def stream_id_to_url(stream_id):
    return str(stream_id).replace(': ', '-').replace(', ', '-').replace('[', '').replace(']', '').replace('=', '-')\
        .replace(':', '')


def treelib_to_treeview(d):
    root = []

    def transform(node, link=''):
        nodes = []
        for item in node:
            if not link:
                link = '/view?'
            else:
                link += '&'
            text = "{}={}".format(item, node[item]['data'])
            link += text
            dd = dict(text=text, href=link)
            if 'children' in node[item]:
                # dd['nodes'] = [dict(text='x', nodes=transform(child)) for child in node[item]['children']]
                dd['nodes'] = list(itertools.chain(*[transform(child, link) for child in node[item]['children']]))
            nodes.append(dd)
        return nodes

    for v in d['root']['children']:
        root.append(dict(text="root", nodes=transform(v)))

    return root


class ListConverter(BaseConverter):
    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(super(ListConverter, self).to_url(value) for value in values)


class ParameterListConverter(BaseConverter):
    def to_python(self, value):
        items = value.split('+')
        return [x.split(":") for x in items]

    def to_url(self, values):
        return '+'.join(super(ParameterListConverter, self).to_url("{}:{}".format(*value)) for value in values)


class DictConverter(BaseConverter):
    def to_python(self, value):
        items = value.split('+')
        return dict(x.split("=") for x in items)

    def to_url(self, values):
        return '+'.join(super(DictConverter, self).to_url("{}={}".format(k, v)) for k, v in values.items())


class DatetimeConverter(BaseConverter):
    def to_python(self, value):
        if value.upper() in ('0', 'MIN_DATE', 'MIN', '0-0-0'):
            dt = MIN_DATE
        elif value.upper() == 'NOW':
            dt = utcnow()
        elif value.upper() in ('MAX_DATE', 'MAX'):
            dt = MAX_DATE
        else:
            dt = ciso8601.parse_datetime(value)

        if dt is None:
            raise ValueError("{} not parsed".format(value))

        return dt.replace(tzinfo=UTC)

    def to_url(self, value):
        return value.isoformat()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial

    raise TypeError("Type {} not serializable".format(str(type(obj))))


def json_response(data):
    return Response(json.dumps(data, default=json_serial, iterable_as_array=True), mimetype="application/json")


def csv_response(data):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output


def xml_response(data):
    # root = ET.element('root')  # name the root whatever you want
    # add your data to the root node in the format you want
    # return app.response_class(ET.dump(root), mimetype='application/xml')
    raise TypeError("XML not yet supported")


ENDPOINTS = {
    "json": json_response,
    "csv": csv_response,
    "xml": xml_response
}


KNOWN_TYPES = {
    'int': int,
    'float': float,
    'str': str,
    'bool': bool
}
