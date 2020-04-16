import os

from docker_stats import DockerStatsBot


if __name__ == '__main__':
    _token = os.environ["VL_TOKEN"]
    _channel = int(os.environ["VL_CHANNEL"])
    _ticks = int(os.environ["VL_TICKS"])

    _bot = DockerStatsBot(_token, _channel)

    while True:
        for _ in range(_ticks):
            _bot.graph_loop_tick()

        _bot.plot()
        _bot.graph_reset()
