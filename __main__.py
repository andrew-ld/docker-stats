import os

from voiplocker_stats import VoipLockerStatsBot


if __name__ == '__main__':
    _prefix = os.environ["VL_PREFIX"]
    _token = os.environ["VL_TOKEN"]
    _channel = int(os.environ["VL_CHANNEL"])
    _ticks = int(os.environ["VL_TICKS"])

    _bot = VoipLockerStatsBot(_prefix, _token, _channel)

    while True:
        for _ in range(_ticks):
            _bot.graph_loop_tick()

        _bot.plot()
        _bot.graph_reset()
