from ..tasks import AutomatedTask, TaskStatus


class F1ModelPersistentIdentifier(AutomatedTask):

    def evaluate(self, data: dict):
        if "id" in data:
            return TaskStatus.success
        else:
            return TaskStatus.failed
