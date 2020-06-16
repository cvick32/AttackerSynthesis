import os
import subprocess
import sys
from glob import glob

"""
Functions for dealing with SPIN and SPIN outputs.
"""


def run_spin(modelFile, maxDepth=10000):
    args = "spin -run -a -m " + str(maxDepth) + " -RS88 " + modelFile
    args = [a.strip() for a in args.split(" ")]
    args = [a for a in args if len(a) > 0]
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        stdout = str(stdout)
        if not stdout:
            return False
        if "depth too small" in stdout:
            print(
                "Search depth was too small at " + str(maxDepth), " doubling depth ..."
            )
            return run_spin(modelFile, maxDepth * 2)
        return not ("violated" in stdout or "acceptance cycle" in stdout)
    except Exception as e:
        raise e


def make_all_trails(modelFile, numTrails=100):
    args = ""
    if numTrails <= 1:
        args = "spin -run -a " + modelFile
    else:
        args = "spin -run -a -e -c" + str(numTrails - 1) + " " + modelFile
    subprocess.run(args.split(" "))


def generate_trail_commands(tmpName):
    args = "spin -t -s -r " + tmpName
    args = args.split(" ")
    num = len(glob(tmpName + "*.trail"))
    if num == 0:
        return []
    elif num == 1:
        return [args]
    else:
        return [add_trail_number_to_args(args, i) for i in range(0, num)]


def add_trail_number_to_args(args, num):
    ret = []
    for arg in args:
        if arg != "-t":
            ret.append(arg)
        else:
            ret.append(arg + str(num))
    return ret


def parse_all_trails(spin_cmds, with_recovery=False, debug=False):
    """
    Runs the spin command to retrieve the trail and parses it.
    """
    ret = []
    for cmd in spin_cmds:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        output = str(stdout).strip().replace("\\n", "\n").replace("\\t", "\t")
        parsed = parse_trail(output)
        ret.append(parsed)
    return ret


def parse_trail(trailBody):
    """
    Parses output of reading trail using Spin.
    This will have to change when abstracted away from rendezvous 
    """
    ret, i = [[], []], 0
    for line in trailBody.split("\n"):
        if "(daisy:" in line:
            # https://stackoverflow.com/a/29571669/1586231
            LL = line.rstrip("*")
            chan = LL[line.rfind("(") + 1 : -1]
            msg, evt = None, None
            if "Recv " in line:
                msg = LL[line.rfind("Recv ") + 5 :].split()[0]
                evt = "?"
            elif "Send" in line:
                msg = LL[line.rfind("Send ") + 5 :].split()[0]
                evt = "!"
            if evt != None and msg != None:
                ret[i].append(chan + " " + evt + " " + msg)
        elif "CYCLE" in line:
            i = 1
    return ret
