import functools
import io
import itertools
import docker
import telegram
import typing
import datetime
import multiprocessing.pool
import sys

import matplotlib.pyplot as plt
from matplotlib import ticker as mtick
from matplotlib import dates as mdates
from matplotlib.figure import Figure


def _calculate_cpu_percent(d: dict) -> typing.List[float]:
    cpu_deltas = []

    cores = d["cpu_stats"]["online_cpus"]
    cpu_usage_list = d["cpu_stats"]["cpu_usage"]["percpu_usage"][:cores]
    percpu_usage_list = d["precpu_stats"]["cpu_usage"]["percpu_usage"][:cores]

    for cpu_usage, precpu_usage in zip(cpu_usage_list, percpu_usage_list):
        cpu_delta = float(cpu_usage) - float(precpu_usage)

        if cpu_delta > 0.0:
            cpu_delta /= 10000000.0
        
        cpu_deltas.append(cpu_delta)

    return cpu_deltas


class DockerStatsBot:
    _bot: telegram.Bot
    _channel: int
    _x_data: typing.List[datetime.datetime]
    _y_data: typing.Dict[str, typing.List[typing.List[float]]]
    _docker: docker.APIClient
    _containers: typing.Dict[str, typing.Any]
    _thread_pool: multiprocessing.pool.ThreadPool

    def __init__(self, token: str, channel: int):
        self._channel = channel

        self._bot = telegram.Bot(token=token)
        self._docker = docker.APIClient()

        self._containers = {}

        for container in self._docker.containers():
            if container["State"] == "running":
                name = container["Names"][0]
                self._containers[name] = container["Id"]

        self._thread_pool = multiprocessing.pool.ThreadPool(len(self._containers))

        self.graph_reset()

    def graph_reset(self):
        self._x_data = []
        self._y_data = dict((n, []) for n in self._containers.keys())

    def graph_loop_tick(self):
        self._x_data.append(datetime.datetime.now())

        f = functools.partial(self._docker.stats, stream=False)
        results = self._thread_pool.map(f, self._containers.values())

        for c_name, stats in zip(self._containers.keys(), results):
            self._y_data[c_name].append(_calculate_cpu_percent(stats))

    def plot(self):
        fig: Figure = plt.figure()
        fig.set_size_inches(19, 12)
        fig.subplots_adjust(hspace=0.25, top=0.95, right=0.80, left=0.05, bottom=0.05)

        cores = multiprocessing.cpu_count()

        lines = cores // 3
        rows = cores // lines

        axs = fig.subplots(rows, lines)

        for core, ax in enumerate(itertools.chain.from_iterable(axs)):
            max_cpu = 0

            for label, values in self._y_data.items():
                core_values = [v[core] for v in values]
                max_cpu = max(max_cpu, *core_values)

                if sum(core_values) / len(core_values) >= 0.1:
                    ax.plot(self._x_data, core_values, label=label)

                else:
                    ax.plot(self._x_data, [-sys.maxsize] * len(core_values), label=label)

            ax.set_ylim([0, max_cpu + 10])
            ax.set_xlim([min(self._x_data), max(self._x_data)])

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

            ax.grid(True)
            ax.title.set_text(f"CPU{core + 1}")

        axs[0][-1].legend(self._y_data.keys(), bbox_to_anchor=(1.04, 1), loc="upper left")

        output = io.BytesIO()
        plt.savefig(output, format="png")
        output.seek(0)

        self._bot.send_photo(self._channel, output)

        plt.close(fig)
        output.close()


__all__ = [
    "DockerStatsBot"
]
