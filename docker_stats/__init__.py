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


def _calculate_cpu_percent(d: dict) -> float:
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])

    if cpu_delta > 0.0:
        cpu_delta /= float(d["cpu_stats"]["online_cpus"])
        cpu_delta /= 10000000.0

    return cpu_delta


class DockerStatsBot:
    _bot: telegram.Bot
    _channel: int
    _x_data: typing.List[datetime.datetime]
    _y_data: typing.Dict[str, typing.List[float]]
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
        ax = fig.add_subplot(adjustable="box")
        lines = []

        for label, values in self._y_data.items():
            p, = ax.plot(self._x_data, values, label=label)
            lines.append(p)

        ax.get_yaxis().set_major_formatter(mtick.PercentFormatter(decimals=0))
        ax.legend(lines, [l.get_label() for l in lines], bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.gcf().axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        ax.grid(True)
        plt.xticks(rotation=45)

        ax.set_ylim([-2, 102])
        ax.set_xlim([min(self._x_data), max(self._x_data)])

        plt.subplots_adjust(left=0)
        fig.autofmt_xdate()
        plt.tight_layout()

        output = io.BytesIO()
        plt.savefig(output, format="png")
        output.seek(0)

        self._bot.send_photo(self._channel, output)

        plt.close(fig)
        plt.close()


__all__ = [
    "DockerStatsBot"
]
