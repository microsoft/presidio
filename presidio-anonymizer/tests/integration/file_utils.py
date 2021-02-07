import os
from pathlib import Path


def get_scenario_file_content(scenario_method, scenario_name: str):
    integration_directory = Path(__file__).parent
    with open(
        os.path.join(integration_directory, "resources", scenario_method, scenario_name)
    ) as f:
        return f.read()
