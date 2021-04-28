import json
import logging
import os.path
from pathlib import Path
import pandas as pd


def log_message(message):
    """
    Function that manages the logging, in the sense that everything is
    directly logged into statusbar and the log file at once as well as
    printed to the console instead of having to call multiple functions.
    """
    # self.statusbar.showMessage(message, 10000000)
    logging.info(message)
    print(message)


def read_global_settings(default=False):
    """
    Read in global settings from file. The file can be changed using the
    settings window.
    """
    # Load from file to fill the lines
    with open(
        os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json")
    ) as json_file:
        data = json.load(json_file)
    if default == False:
        try:
            settings = data["overwrite"]

            # Update statusbar
            log_message("Global Settings Read from File")
        except:
            settings = data["default"]

            # Update statusbar
            log_message("Default device parameters taken")
    else:
        settings = data["default"]

    for key in settings.keys():
        try:
            settings[key] = float(settings[key])
        except:
            settings[key] = str(settings[key])

        if settings[key] == "True":
            settings[key] = True
        elif settings[key] == "False":
            settings[key] = False

    return settings


def save_file(df, file_path, header_lines, save_header=False):
    """
    Generic function that allows to save a file. If it exists already, rename
    it.
    """
    # First check if file already exists. If yes, add a number at the end (this
    # is checked as often as the file still exists to count up the numbers)
    i = 2
    while True:
        if not os.path.isfile(file_path):
            break

        # Get rid of file ending
        if i == 2:
            file_path = os.path.splitext(file_path)[0] + "_" + f"{i:02d}" + ".csv"
        else:
            # Since we already added a new _no to the file we have to get rid of it again
            file_path = "_".join(file_path.split("_")[:-1]) + "_" + f"{i:02d}" + ".csv"

        i += 1

    with open(file_path, "a") as the_file:
        the_file.write("\n".join(header_lines))

    # Now write pandas dataframe to file
    df.to_csv(file_path, index=False, mode="a", header=save_header, sep="\t")
