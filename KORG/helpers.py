import os
from glob import glob


def negate_claim(phi):
    """
	Given a path to a given LTL specificiationm, phi, negate
	phi and write it to a file called "negated.pml".
	"""
    contents = file_read(phi)
    if contents == None or contents == False:
        return False
    negated = False
    with open("negated.pml", "w") as fw:
        for l in contents:
            fw.write(l)
            if (not negated) and l == "{":
                fw.write("!")
                negated = True
    return negated


def coalesce(file_list, name):
    """
	Given a list of paths to a model and a property, puts them all 
	into one runnable promela file.
	INPUT:
		file_list: list of strings with paths to promela files
	OUTPUTS:
		a string that is the path to a file where the contents of the 
		arguments has been dumped to a single file
	"""
    final_content = ""
    for promela_file in file_list:
        with open(promela_file, "r") as f:
            final_content += f.read()
            final_content += "\n"

    with open(name, "w") as fw:
        fw.write(final_content)
    assert os.path.isfile(name)
    return name


def get_IO(IOfile):
    """
	Given an IO specification for a network, Q, return 
	a list of the input and output events. 

	format is like ...

	[chanName]:
		I: [inputs]
		O: [outputs]
	"""
    events = set()
    chan = None
    lineType = lambda x: 2 if "O:" in x else 1 if "I:" in x else 0
    try:
        with open(IOfile, "r") as fr:
            for line in fr:
                j = lineType(line)
                parts = [a.strip() for a in line.split(":")]
                parts = [p for p in parts if len(p) > 0]
                if j == 0:
                    chan = parts[0]
                    continue
                part2 = (
                    [] if len(parts) < 2 else [a.strip() for a in parts[1].split(",")]
                )
                part2 = list(set(part2))
                for msg in part2:
                    if j == 1 and chan != None:
                        events.add(chan + "?" + msg + ";")
                    elif j == 2 and chan != None:
                        events.add(chan + "!" + msg + ";")
        return events
    except Exception:
        return None


def inner_contents(singleModelBody):
    """
	This method returns the body of the given 
	model, as an array. The body is between the 
	two curly brace { }. 
	We assume no comments in the model at the moment ... 
	same with in the properties.
	"""
    if singleModelBody == False:
        return False
    i, j = 0, len(singleModelBody) - 1
    while singleModelBody[i] != "{" and i < len(singleModelBody):
        i += 1
    while singleModelBody[j] != "}" and j > 0:
        j -= 1
    if i >= j or singleModelBody[i] != "{" or singleModelBody[j] != "}":
        return None
    return singleModelBody[i + 1 : j]


def file_write(path, contents):
    with open(path, "w") as fw:
        fw.write(contents)


def file_read(fileName):
    try:
        txt = None
        with open(fileName, "r") as fr:
            txt = fr.read()
        return txt
    except Exception:
        return False


def clean_up_targeted(target):
    files = glob(target)
    for file in files:
        os.remove(file)


def clean_up():
    clean_up_targeted("*.trail")
    clean_up_targeted("*tmp*")
    clean_up_targeted("pan")
    clean_up_targeted("*.pml")
    clean_up_targeted("._n_i_p_s_")
