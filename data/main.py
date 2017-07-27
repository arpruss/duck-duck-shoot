from . import prepare,tools
from .states import title_screen, gameplay, count_up, help_screen, level_editor

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"TITLE": title_screen.TitleScreen(),
                   "GAMEPLAY": gameplay.Gameplay(),
                   "COUNT_UP": count_up.CountUp(),
                   "HELP": help_screen.HelpScreen(),
                   "EDITOR": level_editor.LevelEditor()}
    controller.setup_states(states, "TITLE")
    controller.main()

