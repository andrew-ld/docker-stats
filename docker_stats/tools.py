import typing

import docker as docker

from .container_stats import ContainerStats


def containers_factory(d: docker.APIClient) -> typing.List[ContainerStats]:
    result = []

    for c in d.containers():
        if c["State"] == "running":
            info = d.inspect_container(c["Id"])
            labels = info["Config"]["Labels"]

            try:
                label = labels["plot.label"]
                color = labels["plot.color"]
            except KeyError:
                pass
            else:
                result.append(ContainerStats(label, c["Id"], color))

    return result


def calculate_memory_usage(d: dict) -> int:
    return d["memory_stats"]["usage"] / 1000000


def calculate_cpu_percent(d: dict) -> typing.List[float]:
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
