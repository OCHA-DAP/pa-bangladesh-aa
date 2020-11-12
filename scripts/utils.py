import yaml
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('adm_level', help='Admin level to calculate flood fraction')
    args = parser.parse_args()
    return args


def parse_yaml(filename):
    with open(filename, "r") as stream:
        config = yaml.safe_load(stream)
    return config
