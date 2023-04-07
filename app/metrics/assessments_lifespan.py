import re

from contextlib import asynccontextmanager
from fastapi import FastAPI
from csv import DictReader

from app.models import Indicator

fair_indicators = {}


@asynccontextmanager
async def get_tasks_definitions(app: FastAPI):
    regex = re.compile("^CA\-RDA\-([FAIR][1-9](\.[0-9])?)\-")

    def parse_line(line):
        sub_group = regex.search(line["TaskName"]).groups()[0]
        task_group = sub_group[0]
        return {
            line["TaskName"]: Indicator(
                name=line["TaskName"],
                group=task_group,
                sub_group=sub_group,
                priority=line["TaskPriority"].lower(),
                question=line["TaskQuestion"],
                short=line["TaskShortDescription"],
                description=line["TaskDetails"]
            )
        }

    # Get the list of tasks and their definitions from internal file
    with open("app/metrics/metrics.csv", "r") as file_handler:
        csv_reader = DictReader(file_handler, dialect="unix")
        [fair_indicators.update(parse_line(line)) for line in csv_reader]

    yield
