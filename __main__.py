import json
import os

from docker_stats import DockerStatsBot


if __name__ == '__main__':
    _token = os.environ["DS_TOKEN"]
    _channel = int(os.environ["DS_CHANNEL"])
    _ticks = int(os.environ["DS_TICKS"])

    _bot = DockerStatsBot(_token, _channel)

    while True:
        _bot.fetch_containers()
        _bot.cleanup()

        try:
            for _ in range(_ticks):
                _bot.graph_loop_tick()
        except json.decoder.JSONDecodeError:
            pass
        else:
            _bot.plot()
