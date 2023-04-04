from contextlib import asynccontextmanager
from fastapi import FastAPI
from csv import DictReader

from app.models import TaskDescription

fair_assessments = {}


@asynccontextmanager
async def get_tasks_definitions(app: FastAPI):
    def parse_line(line):
        return {
            line["TaskName"]: TaskDescription(
                name=line["TaskName"],
                priority=line["TaskPriority"].lower(),
                question=line["TaskQuestion"],
                short=line["TaskShortDescription"],
                description=line["TaskDetails"]
            )
        }

    # Get the list of tasks and their definitions from internal file
    with open("app/metrics/metrics.csv", "r") as file_handler:
        csv_reader = DictReader(file_handler, dialect="unix")
        [fair_assessments.update(parse_line(line)) for line in csv_reader]

    print(fair_assessments)
    yield
