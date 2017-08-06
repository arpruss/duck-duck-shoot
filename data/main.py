from . import prepare,tools
from .states import title_screen, level_start, gameplay, count_up, help_screen, level_editor, menu_screen, level_select

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"TITLE": title_screen.TitleScreen(),
                  "LEVEL_START": level_start.LevelStart(),
                  "GAMEPLAY": gameplay.Gameplay(),
                  "COUNT_UP": count_up.CountUp(),
                  "HELP": help_screen.HelpScreen(),
                  "EDITOR": level_editor.LevelEditor(),
                  "MENU": menu_screen.MenuScreen(),
                  "LEVEL_SELECT": level_select.LevelSelectScreen()}
    controller.setup_states(states, "TITLE")
    controller.main()