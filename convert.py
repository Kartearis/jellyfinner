# Unfold subs folder
# Find changing part of name (without exception)
# Build se from it and build new file name (Also drop any [])
import argparse
import shutil
import os
import re


# May have problems in case several sub folders contain subs with identical filenames
def unfold_subs(path):
    files = os.listdir(path)
    for file in files:
        if re.fullmatch(r'.*subs?.*|.*subtitles.*', os.path.basename(file).lower()):
            for sub_file in os.listdir(os.path.join(path, file)):
                shutil.move(os.path.join(path, file, sub_file), path)
            shutil.rmtree(os.path.join(path, file))


def rebuild_names(path):
    pass


def construct_argparser():
    parser = argparse.ArgumentParser(description='Convert file structure to one expected by jellyfin')
    parser.add_argument('paths', metavar='path', type=str, nargs='+', help='Path to folder for conversion')
    return parser.parse_args()


if __name__ == '__main__':
    args = construct_argparser()
    for path in args.paths:
        unfold_subs(path)




