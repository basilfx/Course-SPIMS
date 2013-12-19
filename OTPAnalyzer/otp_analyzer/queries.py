from django.db import models
from django.db.models import Sum, Count, Min, Max, Avg, Q, F

from otp_analyzer.models import Record

import numpy as np
import pylab

def get_distinct_models():
    return Record.objects \
                 .distinct() \
                 .values_list("model", flat=True)

def get_records_per_model(**lookups):
    return Record.objects \
                 .filter(**lookups) \
                 .values("model") \
                 .annotate(count=Count("id")) \
                 .annotate(min_min_ax=Min("min_ax"), min_min_ay=Min("min_ay"), min_min_az=Min("min_az")) \
                 .annotate(avg_min_ax=Avg("min_ax"), avg_min_ay=Avg("min_ay"), avg_min_az=Avg("min_az")) \
                 .annotate(max_max_ax=Max("max_ax"), max_max_ay=Max("max_ay"), max_max_az=Max("max_az")) \
                 .annotate(avg_max_ax=Avg("max_ax"), avg_max_ay=Avg("max_ay"), avg_max_az=Avg("max_az")) \
                 .order_by("-count")

def records_per_model_to_table(**lookups):
    records = get_records_per_model(**lookups)

    for record in records:
        print "%s & %d & %.2f/%.2f/%.2f & %.2f/%.2f/%.2f \\\\" % (
            record["model"],
            record["count"],
            record["min_min_ax"], record["min_min_ay"], record["min_min_az"],
            record["max_max_ax"], record["max_max_ay"], record["max_max_az"]
        )

def get_average_records_per_model():
    averages = map(lambda x: x["count"], get_records_per_model())
    sums = reduce(lambda x, y: x + y, averages)

    return sums / len(averages)

def get_da2_max_per_model(**lookups):
    return Record.objects \
                 .filter(**lookups) \
                 .values("model") \
                 .annotate(count=Count("id")) \
                 .annotate(sensor_da2_max=Max("sensor_da2_max")) \
                 .order_by("model")

def get_da2_max_per_model_and_rounds(**lookups):
    return Record.objects \
                 .filter(**lookups) \
                 .values("model", "rounds") \
                 .annotate(count=Count("id")) \
                 .annotate(sensor_da2_mins=Min("sensor_da2_max"), sensor_da2_avgs=Avg("sensor_da2_max"), sensor_da2_maxs=Max("sensor_da2_max")) \
                 .order_by("model", "rounds")

def plot_histogram_top_n(n, m, p, **lookups):
    top_n = get_records_per_model(**lookups)[:n]
    data = []
    models = []

    figure = pylab.figure()
    axis = figure.add_subplot(1, 1, 1)

    for n in top_n:
        data.append(map(lambda x: min(x.sensor_da2_max, m), Record.objects.filter(model=n["model"])))
        models.append(n["model"])

    n, bins, patches = axis.hist(data, p, histtype="bar", label=models)

    pylab.grid(True)
    pylab.legend()
    pylab.tight_layout()
    pylab.show()

def plot_histogram_all(m, p, **lookups):
    data = []

    figure = pylab.figure()
    axis = figure.add_subplot(1, 1, 1)

    data.append(map(lambda x: min(x.sensor_da2_max, m), Record.objects.all()))

    n, bins, patches = axis.hist(data, p, histtype="bar")

    # Draw cumulative line
    axis_cum = axis.twinx()
    n = [ float(x) / len(data[0]) * 100.0 for x in np.cumsum(n) ]
    print n, x
    axis_cum.plot(bins, [0.0] + n, 'r--')
    axis_cum.set_ylim([0, 100])
    axis_cum.set_ylabel("Cumulative Frequency (%)")

    pylab.grid(True)
    pylab.legend()
    pylab.tight_layout()
    pylab.show()


def plot_histogram_rounds(**lookups):
    records = Record.objects.filter(**lookups)
    data = {}

    figure = pylab.figure()
    axis = figure.add_subplot(1, 1, 1)

    for record in records:
        if not record.rounds in data:
            data[record.rounds] = []

        data[record.rounds].append(record.sensor_da2_max)

    n, bins, patches = axis.hist(list(data.itervalues()), 15, histtype="bar", label=map(str, data.iterkeys()))

    pylab.grid(True)
    pylab.legend()
    pylab.tight_layout()
    pylab.show()

def plot_cluster():
    records = Record.objects.filter(**lookups)