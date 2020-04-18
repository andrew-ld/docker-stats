import functools
import io
import itertools
import time

import docker
import telegram
import typing
import datetime
import multiprocessing.pool

import matplotlib.pyplot as plt
from matplotlib import ticker as mtick
from matplotlib import dates as mdates
from matplotlib.figure import Figure

from docker_stats.container_stats import ContainerStats
from docker_stats.tools import calculate_cpu_percent, calculate_memory_usage, containers_factory


class DockerStatsBot:
    _bot: telegram.Bot
    _channel: int

    _x_data: typing.List[datetime.datetime]

    _docker: docker.APIClient
    _thread_pool: multiprocessing.pool.ThreadPool = None
    _containers: typing.List[ContainerStats] = None

    def __init__(self, token: str, channel: int):
        self._channel = channel
        self._x_data = []

        self._bot = telegram.Bot(token=token)
        self._docker = docker.APIClient()

    def fetch_containers(self):
        while not self._containers:
            self._containers = containers_factory(self._docker)

            if not self._containers:
                time.sleep(1)

        if self._thread_pool is not None:
            self._thread_pool.close()

        self._thread_pool = multiprocessing.pool.ThreadPool(len(self._containers))

    def graph_loop_tick(self):
        self._x_data.append(datetime.datetime.now())

        f = functools.partial(self._docker.stats, stream=False)
        results = self._thread_pool.map(f, [c.uid for c in self._containers])

        for container, stats in zip(self._containers, results):
            container.add_cpu_stats(calculate_cpu_percent(stats))
            container.add_memory_stats(calculate_memory_usage(stats))

    def cleanup(self):
        self._x_data.clear()

        if self._containers is not None:
            self._containers.clear()

        if self._thread_pool is not None:
            self._thread_pool.close()

    def plot(self):
        fig: Figure = plt.figure()
        fig.set_size_inches(19, 12)
        fig.subplots_adjust(hspace=0.25, top=0.95, right=0.95, left=0.05, bottom=0.05)

        cores = multiprocessing.cpu_count()
        axs = fig.subplots(cores // 2, 2)

        ax_memory = axs[0][0]
        axs_cpu = axs[1:]
        axs[0][-1].axis("off")

        for c in self._containers:
            ax_memory.plot(self._x_data, c.get_memory_stats(), c.color, label=c.name)

        ax_memory.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax_memory.grid(True)
        ax_memory.title.set_text("MEMORY")
        ax_memory.legend(bbox_to_anchor=(1.14, 1.07), loc="upper left", shadow=True,  prop={"size": 20})

        for core, ax in enumerate(itertools.chain.from_iterable(axs_cpu)):
            max_cpu = 0

            for c in self._containers:
                cpu_stats = c.get_cpu_stats(core)
                max_cpu = max(max_cpu, *cpu_stats)
                ax.plot(self._x_data, cpu_stats, c.color, label=c.name)

            ax.set_ylim([0, max_cpu + 3])
            ax.set_xlim([min(self._x_data), max(self._x_data)])

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

            ax.grid(True)
            ax.title.set_text(f"CPU{core + 1}")

        output = io.BytesIO()
        plt.savefig(output, format="png")
        output.seek(0)

        self._bot.send_photo(self._channel, output)

        plt.close(fig)
        output.close()


__all__ = [
    "DockerStatsBot"
]
