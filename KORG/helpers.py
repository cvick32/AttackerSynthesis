import os


def negate_claim(phi):
    """
	Given a path to a given LTL specificiationm, phi, negate
	phi and write it to a file called "negated.pml".
	"""
    contents = fileRead(phi)
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


def file_read(fileName):
    try:
        txt = None
        with open(fileName, "r") as fr:
            txt = fr.read()
        return txt
    except Exception:
        return False


def coalesce(model, phi, N, name):
    """
	Given the paths to a model and a property, puts them all 
	into one runnable promela file.
	INPUT:
		model - the string containing the path to the model file
		phi   - the string containing the path to the ltl model file
		N     - the string containing the path to the N model file
	OUTPUTS:
		a string that is the path to a file where the contents of the 
		arguments has been dumped to a single file
	"""
    fmrLines = ""
    fNrLines = ""
    fprLines = ""

    with open(model, "r") as fmr:
        fmrLines = fmr.read()

    with open(N, "r") as fNr:
        fNrLines = fNr.read()

    with open(phi, "r") as fpr:
        fprLines = fpr.read()

    with open(name, "w") as fw:
        fw.write(fmrLines + "\n" + fNrLines + "\n" + fprLines)

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
