#!/bin/python3
# TODO: Nested subs folders (unfold recursively)
# TODO: Episode numbers like [01]
# TODO: Film mode: no episode/season
import argparse
import shutil
import os
import re

ALL_SUBS = -1
PROVIDE_NUMBER = -1


# May have problems in case several sub folders contain subs with identical filenames
def unfold_subs(path, dry_run = True):
    folders = [folder
             for folder in os.listdir(path)
             if re.fullmatch(r'.*subs?.*|.*subtitles.*', os.path.basename(folder).lower())
               and os.path.isdir(os.path.join(path, folder))]
    if len(folders) == 0:
        print('No subtitle folders found')
        return
    selected_index = 0
    # TODO: Check if input in range
    if len(folders) > 1:
        print('Select which subs to unpack:')
        for index, folder in enumerate(folders):
            print(f"{index:3}) {folder}")
        print(f"{ALL_SUBS:3}) All")
        selected_index = int(input('>>'))
    for index, folder in enumerate(folders):
        if selected_index == ALL_SUBS or index == selected_index:
            for sub_file in os.listdir(os.path.join(path, folder)):
                if sub_file != '.ignore' and os.path.isfile(os.path.join(path, folder, sub_file)):
                    if dry_run:
                        print(f"Copied {os.path.join(path, folder, sub_file)} to {path}")
                    else:
                        shutil.copy(os.path.join(path, folder, sub_file), path)
        # Make jellyfin ignore folder with subs, but leave it in place
        if dry_run:
            print(f"Place .ignore to {path}")
        else:
            open(os.path.join(path, folder, '.ignore'), 'a').close()
        # shutil.rmtree(os.path.join(path, file))


def separate_specials(path, dry_run = True):
    # Consider all names containing sp or special to be specials (and move to subfolder)
    sp_regex = r"[ _.\-\[](sp|special|bonus)[ .\-\]]"
    files = [file
             for file in os.listdir(path)
             if os.path.isfile(os.path.join(path, file)) and re.search(sp_regex, file.lower())]
    if len(files) == 0:
        return
    if dry_run:
        print(f"Create {path}/Specials")
    else:
        try:
            os.mkdir(os.path.join(path, 'Specials'))
        except FileExistsError:
            pass
    for file in files:
        if dry_run:
            print(f"Moved {os.path.join(path, file)} to {os.path.join(path, 'Specials', file)}")
        else:
            shutil.move(os.path.join(path, file),os.path.join(path, 'Specials', file))

def rebuild_names(path, dry_run = True):
    files = [file
               for file in os.listdir(path)
               if os.path.isfile(os.path.join(path, file))]
    for index, value in enumerate(files):
        # later rename actual files
        files[index] = re.sub(r"\[.*?]", '', value)
        if not dry_run:
            shutil.move(os.path.join(path, value), os.path.join(path, files[index]))
    numbers = [match for match in re.finditer(r"\d+", files[0])]
    print(f"Filename format is {files[0]}")
    print('Select number to act as season:')
    for index, match in enumerate(numbers):
        print(f"{index:3}) {match}")
    print(f"{PROVIDE_NUMBER:3}) Provide season number")
    season_group = int(input(">>"))
    if season_group == PROVIDE_NUMBER:
        print("Enter season number")
        season_number = int(input('>>'))
    print('Select number to act as episode:')
    for index, match in enumerate(numbers):
        print(f"{index:3}) {match}")
    episode_group = int(input(">>"))
    # This loop may throw if filenames do not follow one scheme (TODO: handle)
    for index, value in enumerate(files):
        name_parts = []
        episode_numbers = [match for match in re.finditer(r"\d+", value)]
        if season_group != PROVIDE_NUMBER:
            name_parts.append(value[:episode_numbers[season_group].start()] + value[episode_numbers[season_group].end():episode_numbers[episode_group].start()])
        else:
            name_parts.append(value[:episode_numbers[episode_group].start()])
        name_parts.append(value[episode_numbers[episode_group].end():])
        if season_group != PROVIDE_NUMBER:
            season_number = int(episode_numbers[season_group].group(0))
        episode_number = int(episode_numbers[episode_group].group(0))
        new_name = (name_parts[0] + f" s{season_number:02}e{episode_number:02} " + name_parts[1])
        # fix extra spaces
        new_name = re.sub(r"[ \-.]se[ \-.]", ' ', new_name)
        new_name = re.sub(r" \.", ".", re.sub(r" +", " ", new_name)).strip()
        if dry_run:
            files[index] = new_name
        else:
            shutil.move(os.path.join(path, value), os.path.join(path, new_name))
    print('Resulting names:')
    if dry_run:
        print(files)
    else:
        print(os.listdir(path))




def construct_argparser():
    parser = argparse.ArgumentParser(description='Convert file structure to one expected by jellyfin')
    parser.add_argument('paths', metavar='path', type=str, nargs='+', help='Path to folder for conversion')
    return parser.parse_args()


if __name__ == '__main__':
    args = construct_argparser()
    #TODO: Refactor dry-run functionality
    dry_run = False
    for path in args.paths:
        print(f"--Processing folder {path}--")
        unfold_subs(path, dry_run)
        separate_specials(path, dry_run)
        rebuild_names(path, dry_run)




