"""
Multiple WAD Injector

checks for a settings file and:
-  Clones OOTR repo if not already present
-  Then prints a link to it if gz gui is not already present
-  Then requests a settings string if not present
-  Then Requests the number of seeds to generate, if not present

Then loops and generates the roms, followed by injecting them into wad donors
to generate the alloted number of rando seeds

NOTE for some reason no cosmetics or sound changes can be done with this. The settings
     string doesnt change when you update the cosmetics, and the system doesnt apeear to 
     allow for cosmetics/sounds to be update by settings string
"""

import os
import subprocess
import json
import sys
import glob
import shutil
from venv import create

def main():
    # make sure we have all the files we need
    try:
        settings = json.loads(open("./settings.json").read())
    except:
        print("You might have accidentally deleted the default settings.json file, please re-clone!")
        sys.exit()
    
    ootr_path = os.path.abspath(settings["ootr_path"])
    gz_path = os.path.abspath(settings["gz_path"])
    num_seeds = int(settings["num_seeds"])
    ootr_settings = os.path.abspath("./ootr_settings.json")
    rom_path = os.path.abspath(settings["rom_path"])
    wad_path = os.path.abspath(settings["wad_path"])
    ootr_log = os.path.abspath("./log.log")

    # doner rom, clean oot v1.0
    dummy_path = os.path.abspath(".\OoT-Randomizer\ZOOTDEC.z64")

    if not os.path.exists(dummy_path):
        shutil.copy(rom_path, dummy_path)

    print(f"Generating {num_seeds} seeds with settings from '{ootr_settings}'")
    if not os.path.exists(ootr_path):
        print("WARNING: ootr not cloned, run the following to clone it: ")
        print("    git clone https://github.com/TestRunnerSRL/OoT-Randomizer.git")   
        print("then run me again :)")
        sys.exit()
    if len(glob.glob("./gz*")) == 0:
        print("WARNING: you dont not have gz (for wad injection)")
        print("download it from here: https://github.com/glankk/gz/releases")
        print("Extract it in this repo's root directory, should be called something like 'gz-0.3.6-windows-i686'")
        print("Then run me again :)")
        sys.exit()
    

    sys.path.extend(".\\OoT-Randomizer")
    
    # Generate the rando seed roms
    created_roms = []
    for i in range(num_seeds):
        print(f"Creating seed number {str(i+1)}")
        stdout = subprocess.check_output(["python", ".\\OoT-Randomizer\\OoTRandomizer.py", 
                                          "--settings", ootr_settings, "1>", ootr_log, "2>&1"], 
                                         shell=True, encoding="utf8")
        for line in open(ootr_log, 'r').readlines():
            if "Created compressed rom at" in line:
                filename = line.split("at:")[1].strip()
                created_roms.append(filename)
                print(f"Finished '{filename}'")

    # Inject them into wad to make wii vc wads of the rando seeds
    if os.path.exists("./output"):
        shutil.rmtree("./output")
    os.mkdir("./output")
    home = os.getcwd()
    os.chdir(gz_path)
    cur = 1
    patcher = os.path.abspath("./patch-wad.bat")
    for rom in created_roms:
        new_path = os.path.abspath(f"./output/OOTR{str(cur)}.wad")
        command = [patcher, '-m', rom, '-o', new_path, wad_path]
        print(f"running: '{' '.join(command)}'")
        subprocess.check_output(command)
        cur += 1
        print(f"created '{new_path}'")



if __name__ == "__main__":
    main()