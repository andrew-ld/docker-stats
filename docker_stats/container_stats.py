import typing


class ContainerStats:
    _cpu_stats: typing.List[typing.List[float]]
    _memory_stats: typing.List[float]
    _name: str
    _uid: str
    _color: str

    def __init__(self, name: str, uid: str, color: str):
        self._name = name
        self._uid = uid
        self._color = color
        self._cpu_stats = []
        self._memory_stats = []

    def get_memory_stats(self) -> typing.List[float]:
        return self._memory_stats

    def get_cpu_stats(self, core: int) -> typing.List[float]:
        return [stats[core] for stats in self._cpu_stats]

    def add_cpu_stats(self, stats: typing.List[float]):
        self._cpu_stats.append(stats)

    def add_memory_stats(self, usage: int):
        self._memory_stats.append(usage)

    def cleanup(self):
        self._cpu_stats.clear()
        self._memory_stats.clear()

    @property
    def name(self) -> str:
        return self._name

    @property
    def uid(self) -> str:
        return self._uid

    @property
    def color(self) -> str:
        return self._color

    def __repr__(self) -> str:
        return repr((
            self._cpu_stats,
            self._memory_stats
        ))

    def __str__(self) -> str:
        return repr(self)
