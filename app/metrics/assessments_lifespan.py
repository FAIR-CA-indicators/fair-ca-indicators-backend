import re

from contextlib import asynccontextmanager
from fastapi import FastAPI
from csv import DictReader

import app.models as models

fair_indicators = {}


@asynccontextmanager
async def get_tasks_definitions(app: FastAPI):
    """
    Method to parse `metrics.csv` and load its content in memory for use by `app`
    NB: This method is loaded in app lifespan. See [lifespan events](https://fastapi.tiangolo.com/advanced/events/)

    :param app: The FastAPI application that will use the content of `metrics.csv`
    :return: None
    """
    regex = re.compile(r"^CA-RDA-([FAIR][1-9](\.[0-9])?)-")

    def parse_line(line):
        sub_group = regex.search(line["TaskName"]).groups()[0]
        task_group = sub_group[0]
        return {
            line["TaskName"]: models.Indicator(
                name=line["TaskName"],
                group=task_group,
                sub_group=sub_group,
                priority=line["TaskPriority"].lower(),
                question=line["TaskQuestion"],
                short=line["TaskShortDescription"],
                description=line["TaskDetails"],
            )
        }

    # Get the list of tasks and their definitions from internal file
    with open("app/metrics/metrics.csv", "r") as file_handler:
        csv_reader = DictReader(file_handler, dialect="unix")
        [fair_indicators.update(parse_line(line)) for line in csv_reader]

    yield
