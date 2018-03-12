from current_work.utils.load_config import load_config
from current_work.look_labels_app import LookLabelAPP


def main():
    config = load_config()

    LookLabelAPP(config=config)


if __name__ == '__main__':
    main()
