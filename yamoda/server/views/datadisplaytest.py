#  -*- coding: utf-8 -*-
#
# yamoda, (c) 2012, see AUTHORS.  Licensed under the GNU GPL.

import os
import logging as logg
from collections import namedtuple
from numpy.random import randint, random
from numpy import arange, average, std, meshgrid, ndarray, sin, cos
from matplotlib.pylab import imsave, imshow, savefig, colorbar, figure
import matplotlib
from flask import render_template, make_response, request, abort, jsonify
from flask.ext.login import login_required
from yamoda.server import app
from yamoda.server.database import Data, Entry, Context
from yamoda.server import db


def count(value):
    """Number of elements
    :returns: "scalar" or number of elements for ndarrays 
    """
    if isinstance(value, float) or isinstance(value, int):
        return "scalar"
    if isinstance(value, ndarray):
        return len(value.flat)
    else:
        return "unknown"




def create_example_2D_plot(func, pos):
    """Create 2d image plot with colorbar and save to file as png
    """
    arr = arange(-5, 5, 0.1)
    xx, yy = meshgrid(arr, arr)
    img = func(xx, yy)
    # save image
    filepath = os.path.join(os.getcwd(), *["yamoda", "server", "static", "entry_{}.png".format(pos)])
    logg.debug("saving image to file %s", filepath)
    fig = figure()
    ax = fig.gca()
    ax_image = ax.imshow(img)
    fig.colorbar(ax_image)
    ax.grid(1)
    fig.savefig(filepath, format="png", bbox_inches='tight', transparent=True)
    return img


@app.route("/datadisplaytest")
def datadisplaytest():
    """Create and return some fake values for sparkline and matplotlib testing
    """
    data = []
    fakeentry = namedtuple("FakeEntry", "id parameter_name parameter_visible, shape value unit lower avg upper")
    params = [
              ("t1", "s", 30, False),
              ("T1", u"°C", 30, True),
              ("t2", "s", 100, False),
              ("T2", u"°C", 100, True),
              ("t3", "s", 300, False),
              ("T3", u"°C", 300, True),
    ]

    for pos, (name, unit, count, visible) in enumerate(params):
        if pos % 2 == 0:
            value = arange(0, count / 10., 0.1)
            avg = lower = upper = 0
            shape = [count]
        else:
            value = random([count]) * 100 - 50
            avg = average(value)
            std_ = std(value)
            shape = [count]
            lower = avg - 1 * std_
            upper = avg + 1 * std_
        data.append(fakeentry(pos, name, visible, shape, value, unit, lower, avg, upper))

    # scalar test
    data.append(dict(id=6, parameter_name="v", value=23, unit="m/s"))

    # 2D test
    img = create_example_2D_plot(lambda x, y: x ** 2 + y ** 2, 7)
    data.append(dict(id=7, parameter_name="x**2 + y**2", parameter_visible=True, value=img, unit="", shape=img.shape))
    img2 = create_example_2D_plot(lambda x, y: sin(x) + cos(y), 8)
    data.append(dict(id=8, parameter_name="sin(x) + cos(y)", parameter_visible=False, value=img2, unit="", shape=img2.shape))
    img3 = create_example_2D_plot(lambda x, y: random([100, 100]), 9)
    data.append(dict(id=9, parameter_name="random noise", parameter_visible=True, value=img3, unit="", shape=img3.shape))
    data.append(dict(id=10, parameter_name="X", parameter_visible=True, value=42, unit="F"))
    ctx_id = db.session.query(Context.id).filter_by(name="1DContext").subquery()
    data1D = Data.query.filter(Data.context_id == ctx_id).first()
    for entry in data1D.entries:
        data.append(dict(id=10 + entry.id, parameter_name=entry.parameter.name, parameter_visible=entry.parameter.visible, value=entry.value, unit=entry.parameter.unit, shape=entry.value.shape))

    return render_template("datadisplaytest.html", data=data, test=(1, 2))
