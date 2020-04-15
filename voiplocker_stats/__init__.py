import io

import docker
import telegram
import typing
import datetime

import matplotlib.pyplot as plt
from matplotlib import ticker as mtick
from matplotlib import dates as mdates


def _calculate_cpu_percent(d: dict) -> float:
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])

    if cpu_delta > 0.0:
        cpu_delta /= 10000000

    return cpu_delta


class VoipLockerStatsBot:
    _bot: telegram.Bot
    _channel: int
    _x_data: typing.List[datetime.datetime]
    _y_data: typing.Dict[str, typing.List[float]]
    _docker: docker.APIClient
    _containers: typing.Dict[str, typing.Any]

    def __init__(self, prefix: str, token: str, channel: int):
        self._channel = channel

        self._bot = telegram.Bot(token=token)
        self._docker = docker.APIClient()

        self._containers = {}

        for container in self._docker.containers():
            if container["State"] == "running":
                if container["Names"][-1].startswith(prefix):
                    name: str = container["Names"][-1]
                    name = name.replace(prefix, "")
                    name = "_".join(name.split("_")[0:-1])
                    self._containers[name] = container["Id"]

        self.graph_reset()

    def graph_reset(self):
        self._x_data = []
        self._y_data = dict((n, []) for n in self._containers.keys())

    def graph_loop_tick(self):
        self._x_data.append(datetime.datetime.now())

        for c_name, c_id in self._containers.items():
            container = self._docker.stats(c_id, stream=False)
            self._y_data[c_name].append(_calculate_cpu_percent(container))

    def plot(self):
        fig, ax = plt.subplots()
        lines = []

        for label, values in self._y_data.items():
            p, = ax.plot(self._x_data, values, label=label)
            lines.append(p)

        ax.get_yaxis().set_major_formatter(mtick.PercentFormatter(decimals=0))
        ax.legend(lines, [l.get_label() for l in lines], bbox_to_anchor=(0.96, 0.96))
        ax.set_ylim([-2, 102])
        ax.grid(True)

        plt.gcf().axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        plt.xticks(rotation=45)
        plt.tight_layout()
        fig.autofmt_xdate()

        output = io.BytesIO()
        plt.savefig(output, format="png")
        output.seek(0)

        self._bot.send_photo(self._channel, output)


__all__ = [
    VoipLockerStatsBot
]
