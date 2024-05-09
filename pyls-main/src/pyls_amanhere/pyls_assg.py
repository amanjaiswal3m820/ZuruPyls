import os
import argparse
import json
from datetime import datetime


def load_json(input_json_path):
    with open(input_json_path) as f:
        data = json.load(f)
        return data


def format_size(size):
    suffixes = ['B', 'K', 'M', 'G', 'TB', 'PB']
    i = 0
    while size >= 1024 and i < len(suffixes) - 1:
        size /= 1024.
        i += 1
    val = f"{size:.1f}".rstrip('0').rstrip('.')
    return f"{val}{suffixes[i]}"


def print_simple(dir_contents):
    for content in dir_contents:
        print(content["name"], end=" " * 4)
    print("")


def print_vertical(dir_contents, human_readable):
    for content in dir_contents:
        timestamp = datetime.utcfromtimestamp(content["time_modified"]).strftime("%b %d %H:%M")
        if human_readable:
            size = format_size(content["size"])
        else:
            size = content["size"]
        if content.get('contents'):
            content["permissions"] = 'd' + content["permissions"][1:]
        else:
            content["permissions"] = '-' + content["permissions"][1:]
        print(content["permissions"], "\t", size, "\t", timestamp, "\t", content["name"])


def filter_contents(content_list, filter_by_type, print_all):
    output = []
    for content in content_list:
        if content["name"].startswith(".") and not print_all:
            continue

        if filter_by_type == "dir" and content.get("contents"):
            output.append(content)
        elif filter_by_type == "file" and not content.get("contents"):
            output.append(content)
        elif filter_by_type is None:
            output.append(content)
    return output


def get_relative_path_contents(content_list, relative_path):
    relative_path_list = relative_path.strip("/").split("/")
    if relative_path_list[0] == ".":
        relative_path_list.pop(0)
    if not relative_path_list:
        return content_list

    for path in relative_path_list:
        found = False
        for content in content_list:
            if content["name"] == path:
                if content.get("contents"):
                    content_list = content["contents"]
                else:
                    content_list = [content]
                found = True
                break
        if not found:
            raise Exception(f"cannot access {relative_path}: No such file or directory")
    return content_list


def print_content(dir_contents, args):
    if args.relative_path:
        dir_contents = get_relative_path_contents(dir_contents, args.relative_path)

    dir_contents = filter_contents(dir_contents, args.filter, args.print_all)

    if args.sorted_by_time:
        dir_contents = sorted(dir_contents, key=lambda d: d["time_modified"])
    else:
        dir_contents = sorted(dir_contents, key=lambda d: d["name"])

    if args.reverse:
        dir_contents = dir_contents[::-1]

    if args.vertical:
        print_vertical(dir_contents, args.human_readable)
    else:
        print_simple(dir_contents)


def main():
    parser = argparse.ArgumentParser(
        prog="pyls",
        description="Prints the contents of a json file (which contains the information of a directory in nested "
                    "structure) and prints out its content in the console in  the style of ls (linux utility)",
        add_help=False)
    parser.add_argument("-A", dest='print_all', action="store_true", default=False, help="Prints all the files and "
                                                                                         "directories (including "
                                                                                         "files starting with '.'),")
    parser.add_argument("-l", dest='vertical', action="store_true", default=False, help="Prints the results "
                                                                                        "vertically with additional "
                                                                                        "information.")
    parser.add_argument("-r", dest="reverse", action="store_true", default=False, help="Display the results in reverse.")
    parser.add_argument("-t", dest="sorted_by_time", action="store_true", default=False, help="Prints the results "
                                                                                              "sorted by "
                                                                                              "time_modified (oldest "
                                                                                              "first).")
    parser.add_argument("-h", dest="human_readable", action="store_true", help="Prints the sizes in human readable "
                                                                               "format.")
    parser.add_argument("--filter", choices=("file", "dir"), help="This command will filter the output based on given "
                                                                  "option: file or dir.")
    parser.add_argument("relative_path", nargs="?", type=str, help="Display only the contents of the relative path "
                                                                   "within the input JSON.")
    parser.add_argument('--help', action="help", help="Show this help message and exit")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    json_file_path = (script_dir + "\\structure.json")

    data = load_json(json_file_path)
    top_level_contents = []
    if "contents" in data:
        top_level_contents = data['contents']

    print_content(top_level_contents, args)


if __name__ == "__main__":
    main()
