# Unfold subs folder If several present - ask user (flag)
# Find changing part of name (without exception)
# Build se from it and build new file name (Also drop any [])
# User should be able to provide season number
import argparse
import shutil
import os
import re


# May have problems in case several sub folders contain subs with identical filenames
def unfold_subs(path):
    folders = [folder
             for folder in os.listdir(path)
             if re.fullmatch(r'.*subs?.*|.*subtitles.*', os.path.basename(folder).lower())
               and os.path.isdir(os.path.join(path, folder))]
    print(folders)
    if len(folders) == 0:
        print('No subtitle folders found')
        return
    selected_index = 0
    if len(folders) > 1:
        print('Select which subs to unpack:')
        for index, folder in enumerate(folders):
            print(f"{index}) {folder}")
        selected_index = int(input('>>'))
    for index, folder in enumerate(folders):
        if index == selected_index:
            for sub_file in os.listdir(os.path.join(path, folder)):
                shutil.copy(os.path.join(path, folder, sub_file), path)
        # Make jellyfin ignore folder with subs, but leave it in place
        open(os.path.join(path, folder, '.ignore'), 'a').close()
        # shutil.rmtree(os.path.join(path, file))


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




