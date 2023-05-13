import argparse
import importlib
import os
import sys

from .entrypoint import Entrypoint
from .interface import RosterAgentInterface


# Is there a more standard way to do this?
def import_object(path):
    module_path, object_name = path.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, object_name)


def main():
    parser = argparse.ArgumentParser(description="CLI tool for Roster Agent")
    parser.add_argument(
        "agent_path", type=str, help="Python path to the RosterAgentInterface object"
    )

    args = parser.parse_args()

    # Dynamically import the module and get the agent
    sys.path.insert(0, os.getcwd())
    agent = import_object(args.agent_path)

    # Check if the agent conforms to the RosterAgentInterface
    # TODO: duck typing instead of isinstance
    assert isinstance(
        agent, RosterAgentInterface
    ), "The provided agent does not conform to the RosterAgentInterface"

    # Create and run the entrypoint
    entrypoint = Entrypoint.from_env(agent=agent)
    entrypoint.run()


if __name__ == "__main__":
    main()
