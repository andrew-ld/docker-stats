import json
import os
import time

from docker_stats import DockerStatsBot


if __name__ == '__main__':
    time.tzset()

    _token = os.environ["DS_TOKEN"]
    _channel = int(os.environ["DS_CHANNEL"])
    _ticks = int(os.environ["DS_TICKS"])

    _bot = DockerStatsBot(_token, _channel)

    while True:
        _bot.cleanup()
        _bot.fetch_containers()

        try:
            for _ in range(_ticks):
                _bot.graph_loop_tick()
        except json.decoder.JSONDecodeError:
            pass
        else:
            _bot.plot()
