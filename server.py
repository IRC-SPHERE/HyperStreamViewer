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
from flask import Flask, render_template, request, jsonify
from flask_bower import Bower
from plotting import get_bokeh_plot
import simplejson as json
import os

from bokeh.util.string import encode_utf8

from view_helpers import treelib_to_treeview, custom_sort, custom_format, ListConverter, DictConverter, \
    ParameterListConverter, DatetimeConverter, ENDPOINTS, KNOWN_TYPES, stream_id_to_url

from hyperstream import HyperStream, Tool, TimeInterval
from hyperstream.utils import MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError, \
    ToolInitialisationError


hs = HyperStream()
app = Flask(__name__)
Bower(app)
app.url_map.converters['list'] = ListConverter
app.url_map.converters['params_list'] = ParameterListConverter
app.url_map.converters['dict'] = DictConverter
app.url_map.converters['datetime'] = DatetimeConverter
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.filters['treelib_to_treeview'] = treelib_to_treeview
app.jinja_env.filters['custom_sort'] = custom_sort
app.jinja_env.filters['custom_format'] = custom_format
app.jinja_env.filters['u'] = stream_id_to_url
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def index():
    return render_template("index.html", hyperstream=hs)


# @app.route("/dashboard")
# def dashboard():
#     return render_template("dashboard.html")

@app.route("/plates")
def plates():
    return render_template("plates.html", hyperstream=hs)


@app.route("/meta_data")
def meta_data():
    return render_template("meta_data.html", hyperstream=hs)


@app.route("/channels")
def channels():
    if 'channel_id' in request.args:
        channel_id = request.args['channel_id']
        channel = hs.channel_manager[channel_id]
        s = sorted([(stream_id, str(stream_id)) for stream_id in channel.streams.keys()], key=lambda x: x[1])
        channel_streams = [x[0] for x in s]
    else:
        channel_id = None
        channel_streams = None

    return render_template("channels.html", hyperstream=hs, channel_id=channel_id, channel_streams=channel_streams)


def find_streams(d):
    error = None
    found_streams = None
    try:
        channel = d.pop("channel")
        found_streams = hs.channel_manager[channel].find_streams(**d)
    except KeyError:
        pass
    except (StreamNotFoundError, StreamNotAvailableError) as e:
        pass
        error = e
    return error, found_streams


@app.route("/streams")
def streams():
    d = dict(request.args.items())
    autoreload = d.pop('autoreload', False)
    default_view = d.pop('default_view', None)
    error, found_streams = find_streams(d)
    return render_template("streams.html", hyperstream=hs, streams=found_streams, error=error,
                           default_view=default_view, autoreload=autoreload)


stream_route = "/stream/<channel>/<name>/<dict:meta_data>/"


@app.route(stream_route + "<string:func>/<string:mimetype>/")
@app.route(stream_route + "<string:func>+<params_list:parameters>/<string:mimetype>/")
@app.route(stream_route + "<datetime:start>+<datetime:end>/<string:func>/<string:mimetype>/")
@app.route(stream_route + "<datetime:start>+<datetime:end>/<string:func>+<params_list:parameters>/<string:mimetype>/")
def stream(channel, name, meta_data, mimetype, func, parameters=None, start=None, end=None):
    try:
        stream = hs.channel_manager[channel].find_stream(name=name, **meta_data)
        if start and end:
            ti = TimeInterval(start, end)
            window = stream.window(ti)
        else:
            window = stream.window()

    except (KeyError, TypeError, MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError) as e:
        return jsonify({
            'exception': str(type(e)),
            'message': e.message,
            'data': dict(channel=channel, name=name, meta_data=meta_data, start=start, end=end)
        })

    try:
        if hasattr(window, func):
            if parameters:
                data = getattr(window, func)(*(KNOWN_TYPES[p[0]](p[1]) for p in parameters))
            else:
                data = getattr(window, func)()
            from collections import deque
        else:
            return jsonify({'exception': "Function not available", "message": func})
    except (KeyError, TypeError) as e:
        return jsonify({'exception': str(type(e)), 'message': e.message, 'data': (func, parameters)})

    try:
        return ENDPOINTS[mimetype](data)
    except KeyError as e:
        return jsonify({'exception': str(type(e)), 'message': "Endpoint not found", 'data': mimetype})
    except TypeError as e:
        return jsonify({'exception': str(type(e)), 'message': e.message, 'data': (func, parameters, str(list(data)))})


@app.route("/factors")
def factors():
    error = None
    try:
        factor_id = request.args['factor_id']
        workflow_id = request.args['workflow_id']
        workflow = hs.workflow_manager.workflows[workflow_id]
        factor = [x for x in workflow.factors if x.factor_id == factor_id][0]
    except KeyError as e:
        factor = None
        error = e

    return render_template("factors.html", hyperstream=hs, factor=factor, error=error)


@app.route("/tools")
def tools():
    error = None
    tool = None
    try:
        name = request.args['tool']
        import json
        parameters = json.loads(request.args['parameters'])
        if parameters:
            parameters = Tool.parameters_from_model(Tool.parameters_from_dicts(parameters))
        else:
            # Tools don't expect empty lists
            parameters = None
        tool = hs.channel_manager.get_tool(name=name, parameters=parameters)
    except KeyError:
        pass
    except ToolInitialisationError as e:
        error = e

    return render_template("tools.html", hyperstream=hs, tool=tool, error=error)


@app.route("/workflows")
def workflows():
    return render_template("workflows.html", hyperstream=hs)


@app.route("/views")
def views():
    # error, found_streams = find_streams(dict(request.args.items()))
    # return render_template("streams.html", hyperstream=hs, streams=found_streams, error=error)
    #
    # Load all of the json files in the views folder
    files = []
    errors = []
    for fname in os.listdir("views"):
        if fname.endswith(".json"):
            with open(os.path.join("views", fname)) as f:
                try:
                    files.append(dict(filename=fname, data=json.load(f)))
                except (OSError, IOError, TypeError) as e:
                    errors.append((fname, e))

    return render_template("views.html", hyperstream=hs, views=files, errors=errors)


@app.route("/view")
def view():
    streams = hs.channel_manager.mongo.find_streams(**dict(request.args.items()))
    # return render_template("view.html", streams=streams)
    x = list(range(0, 100))

    plot = get_bokeh_plot(title="Polynomial", x=x, y=list(map(lambda xx: xx ** 2, x)))

    html = render_template(
        'view.html',
        **plot
    )
    return encode_utf8(html)


@app.route("/polynomial")
def polynomial():
    """ Very simple embedding of a polynomial chart
    """
    # Create a polynomial line graph with those arguments
    x = list(range(0, 100))

    plot = get_bokeh_plot(title="Polynomial", x=x, y=list(map(lambda xx: xx ** 2, x)))

    html = render_template(
        'embed.html',
        **plot
    )
    return encode_utf8(html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
