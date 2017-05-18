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
import json
from flask import Flask, render_template, request, abort, jsonify, Response
from flask_bower import Bower
from hyperstream import HyperStream, Tool
from hyperstream.utils import MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError, \
    ToolInitialisationError
from plotting import get_bokeh_plot

from bokeh.util.string import encode_utf8

from view_helpers import treelib_to_treeview, custom_sort, custom_format, ListConverter, DictConverter, json_serial


hs = HyperStream()
app = Flask(__name__)
Bower(app)
app.url_map.converters['list'] = ListConverter
app.url_map.converters['dict'] = DictConverter
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.filters['treelib_to_treeview'] = treelib_to_treeview
app.jinja_env.filters['custom_sort'] = custom_sort
app.jinja_env.filters['custom_format'] = custom_format
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


@app.route("/streams")
def streams():
    error = None
    try:
        d = dict(request.args.items())
        channel = d.pop("channel")
        stream = hs.channel_manager[channel].find_stream(**d)
    except KeyError:
        stream = None
    except (MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError) as e:
        stream = None
        error = e

    return render_template("streams.html", hyperstream=hs, stream=stream, error=error)


@app.route("/stream/<channel>/<name>/<dict:meta_data>/data.json")
def stream(channel, name, meta_data):
    try:
        stream = hs.channel_manager[channel].find_stream(name=name, **meta_data)
        data = stream.window().last(50)
    except (KeyError, TypeError, MultipleStreamsFoundError, StreamNotFoundError, StreamNotAvailableError) as e:
        return jsonify({'exception': str(type(e)), 'message': e.message})

    return Response(json.dumps(data, default=json_serial), mimetype="application/json")


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
