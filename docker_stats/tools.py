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


def calculate_cpu_percent(d: dict) -> float:
    cpu_deltas = []

    cpu_delta = d["cpu_stats"]["cpu_usage"]["total_usage"] - d["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = d["cpu_stats"]["system_cpu_usage"] - d["precpu_stats"]["system_cpu_usage"]
    result_cpu_usage = cpu_delta / system_delta * d["cpu_stats"]["online_cpus"] * 100

    return result_cpu_usage
