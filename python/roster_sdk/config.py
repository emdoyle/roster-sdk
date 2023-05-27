from environs import Env

env = Env()
env.read_env()

# Roster API Config
ROSTER_API_URL = env.str("ROSTER_API_URL", "http://localhost:7888/v0.1")
ROSTER_API_EVENTS_PATH = env.str("ROSTER_API_EVENTS_PATH", "/resource-events")
ROSTER_API_AGENTS_PATH = env.str("ROSTER_API_AGENTS_PATH", "/agents")
ROSTER_API_TASKS_PATH = env.str("ROSTER_API_TASKS_PATH", "/task")
ROSTER_API_CONVERSATIONS_PATH = env.str(
    "ROSTER_API_CONVERSATIONS_PATH", "/conversation"
)
ROSTER_API_ROLES_PATH = env.str("ROSTER_API_ROLES_PATH", "/roles")
ROSTER_API_TEAMS_PATH = env.str("ROSTER_API_TEAMS_PATH", "/teams")
ROSTER_API_TEAM_LAYOUTS_PATH = env.str("ROSTER_API_TEAM_LAYOUTS_PATH", "/team-layouts")
