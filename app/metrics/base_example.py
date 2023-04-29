from fair_test import FairTest, FairTestEvaluation


class MetricTest(FairTest):
    metric_path = "fair-test-example"
    metric_version = "0.1.0"
    title = "Example of FairTest implementation"
    description = """This indicator serves no purpose except being used as a template for other FairCombine tests"""
    topics = ["data"]  # Needs to be standardised!
    authors = "author-orcid"
    test_test = {}  # Contains the urls towards records used for testing the metric

    def execute_metric(self, object):
        return True if object else False

    def evaluate(self, eval: FairTestEvaluation):
        eval.info(
            "Running FairCombine example. This test will pass",
        )

        # Retrieving subject of the evaluation (a model or an archive)
        data = eval.retrieve_metadata(eval.subject)

        # Running some kind of tests on the data (does it contain an id, a license, ...)
        result = self.execute_metric(data)

        return result


class ManualMetricTest(FairTest):
    pass


class AutomaticMetricTest(FairTest):
    pass
