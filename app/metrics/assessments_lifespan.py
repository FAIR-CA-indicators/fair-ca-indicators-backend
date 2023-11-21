import re

from contextlib import asynccontextmanager
from fastapi import FastAPI
from csv import DictReader

from app.dependencies.settings import get_settings
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
    regex_csh = re.compile(r"^CSH-RDA-([FAIR][1-9](\.[0-9])?)-")
    regex_joined = re.compile(r"^(CA-RDA|CSH-RDA)-([FAIR][1-9](\.[0-9])?)-")
    config = get_settings()

    print(config)
    def parse_line(line):
        sub_group = regex_joined.search(line["TaskName"])
        if sub_group is None:
            return
        sub_group = sub_group.groups()[1]
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
    with open(config.indicators_path, "r") as file_handler:
        csv_reader = DictReader(file_handler, dialect="unix")
        for line in csv_reader:
            parsed_line = parse_line(line)
            if parsed_line is not None:
                print(parsed_line)
                fair_indicators.update(parsed_line)
        #[fair_indicators.update(parse_line(line)) for line in csv_reader]

    yield
