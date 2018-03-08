from 查看PTCT及标签数据._utils.load_config import load_config
from 查看PTCT及标签数据.look_labels_app import LookLabelAPP


def main():
    config = load_config()

    LookLabelAPP(config=config)


if __name__ == '__main__':
    main()
