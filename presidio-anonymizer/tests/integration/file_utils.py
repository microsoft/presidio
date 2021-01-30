import os


def get_scenario_file_content(scenario_method, scenario_name: str):
    with open(os.path.join("resources", scenario_method, scenario_name)) as f:
        return f.read()
