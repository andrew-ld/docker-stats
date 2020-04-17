import functools
import io

import docker
import telegram
import typing
import datetime
import multiprocessing.pool

import matplotlib.pyplot as plt
from matplotlib import ticker as mtick
from matplotlib import dates as mdates


def _calculate_cpu_percent(d: dict) -> typing.List[float]:
    cpu_deltas = []

    cpu_usage_list = d["cpu_stats"]["cpu_usage"]["percpu_usage"]
    percpu_usage_list = d["precpu_stats"]["cpu_usage"]["percpu_usage"]

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
        fig = plt.figure()
        fig.set_size_inches(11, 7)
        axs = fig.subplots(2, 3)
        lines = []
        
        ax = axs[0, 0]

        for label, values in self._y_data.items():
            tmp_val = []
            for value in values:
                tmp_val.append(value[0])
            p, = ax.plot(self._x_data, tmp_val, label=label)
            lines.append(p)

        ax.get_yaxis().set_major_formatter(mtick.PercentFormatter(decimals=0))
        fig.legend(lines, [l.get_label() for l in lines], loc="upper right") # , bbox_to_anchor=(1.04, 1)
        plt.gcf().axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        ax.grid(True)
        plt.xticks(rotation=45)

        ax.set_ylim([-2, 102])
        ax.set_xlim([min(self._x_data), max(self._x_data)])

        plt.subplots_adjust(left=0)
        fig.autofmt_xdate()
        plt.tight_layout()

        plt.ioff()
        output = io.BytesIO()
        fig.savefig(output, format="png")
        output.seek(0)

        self._bot.send_photo(self._channel, output)

        output.close()
        plt.close(fig)
        plt.close("all")


__all__ = [
    "DockerStatsBot"
]
