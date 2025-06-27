import argparse
import sys

sys.path.insert(0, "./")

from query_scripts.query_ragflow import query_ragflow
from query_scripts.query_chatwiki import query_chatwiki


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query question.")
    parser.add_argument(
        "--type",
        help="Which Knowledge to choose",
        choices=["ragflow", "dify", "fastgpt", "chatwiki"],
        required=True,
    )
    args = parser.parse_args()

    if args.type == "ragflow":
        query_ragflow(args.type)
    elif args.type == "chatwiki":
        query_chatwiki(args.type)
    else:
        raise Exception("Unsupported type.")
