from current_work.look_labels_app.gui import MainGUI
from current_work.utils.load_config import load_config


def main():
    config = load_config()
    MainGUI(config=config)


if __name__ == '__main__':
    main()
