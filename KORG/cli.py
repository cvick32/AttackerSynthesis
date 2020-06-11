import argparse
from glob import glob
import os
import sys
from problem import Problem
from helpers import negate_claim, coalesce, get_IO


def str_to_bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_args():
    parser = initialize_parser()
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        print(
            "\nNote: *either* --dir *or* (--phi, --P, --Q, and --IO) is "
            + "required.  This is an exclusive-or *either*."
        )
        parser.exit()

    args = parser.parse_args()
    if not (args.dir or (args.phi and args.Q and args.model and args.IO)):
        print(
            "\nNote: *either* --dir *or* (--phi, --P, --Q, and --IO) is "
            + "required.  This is an exclusive-or *either*."
        )
        parser.exit()
    check_args(args)
    return Problem(
        args.P,
        args.Q,
        args.IO,
        args.phi,
        args.max_attacks,
        args.characterize,
        args.recovery,
        args.name,
    )


trails = lambda: glob("*.trail")


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


def add_trail_number_to_args(args, num):
    ret = []
    for arg in args:
        if arg != "-t":
            ret.append(arg)
        else:
            ret.append(arg + str(num))
    return ret


def handleTs(args, name):
    args = args.split(" ")
    num = len(glob(name + "*.trail"))
    if num == 0:
        return []
    elif num == 1:
        return [args]
    else:
        return [add_trail_number_to_args(args, i) for i in range(0, num)]


def trail_parse_CMDs(tmpName):
    args = "spin -t -s -r " + tmpName
    return handleTs(args, tmpName)


def clean_and_exit():
    clean_up()
    exit(1)


def check_args(args):
    """
	Checks some semantic assumptions on our arguments
	"""
    if args.max_attacks == None or args.max_attacks < 1:
        print_invalid_num(args.max_attacks)
        clean_and_exit()

    # Can we negate phi?  This is important.
    if not negate_claim(args.phi):
        print_could_not_negate_claim(args.phi)
        clean_and_exit()

    # Check validity: Does model || Q |= phi?
    if not coalesce(args.P, args.phi, args.Q, args.name + "_model_Q_phi.pml"):
        print_invalid_inputs(args.P, args.phi, args.Q)
        clean_and_exit()

    # Get the IO.  Is it empty?
    if args.IO == None:
        clean_and_exit()

    _IO = get_IO(args.IO)
    if _IO == None or len(list(_IO)) == 0:
        print_zero_IO(args.IO)
        clean_and_exit()


# Error message for if we were handed apparently invalid inputs.
def print_invalid_inputs(model, phi, N):
    print(
        "In order for the problem (model, phi, N) to be non-trivial, we "
        + "require that (model || N) |= phi.  However, this does not appear "
        + "to be the case."
    )


# Error message for if we cannot find any solution.
def print_no_solution(model, phi, N, with_recovery):
    possiblyFinite = "with_recovery" if with_recovery else ""
    print("We could not find any " + possiblyFinite + "(model, (N), phi)-attacker A.")


# Error message when we could not negate the claim phi.
def print_could_not_negate_claim(phi):
    if phi == None:
        print("No property phi provided; giving up.")
    else:
        print("We could not negate the claim in " + phi + "; giving up.")


# Error message when we could not get any inputs or outputs.
def print_zero_IO(IO):
    print("We could not find any inputs or outputs in " + IO + "; giving up.")


# Error message when num is too small
def print_invalid_num(num):
    print("--num option must be > 0, was: " + str(num) + "; giving up.")


def initialize_parser():
    """
	Initialize the parser with required and optional
	arguments
	"""
    parser = argparse.ArgumentParser(
        description="Synthesize a (P, phi)-Attacker.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument(
        "--P",
        metavar="P",
        type=str,
        help="A relative or absolute path to a Promela model of a protocol M "
        + "to be attacked, e.g. demo/TCP.pml.",
        required=False,
    )
    required.add_argument(
        "--phi",
        metavar="phi",
        type=str,
        help="A relative or absolute path to a Promela file containing an LTL "
        + "claim phi about M and N, such that (M || N) |= phi, e.g. "
        + "demo/noHalfOpenConnections.pml.",
        required=False,
    )
    required.add_argument(
        "--Q",
        metavar="Q",
        type=str,
        help="A relative or absolute path to a Promela model of a protocol Q "
        + "to be replaced and recovered-to by our attacker, e.g. "
        + "demo/network.pml.",
        required=False,
    )
    required.add_argument(
        "--IO",
        metavar="IO",
        type=str,
        help="The input-output interface of N, in a yaml-ish format.",
        required=False,
    )
    required.add_argument(
        "--max_attacks",
        metavar="max_attacks",
        default=1,
        type=int,
        help="The maximum number of attackers to generate.",
        required=False,
    )
    optional.add_argument(
        "--with_recovery",
        metavar="with_recovery",
        type=str_to_bool,
        default=False,
        nargs="?",
        const=True,
        help="True iff you want the recovered attackers to be attackers with "
        + "recovery, else false.",
        required=False,
    )
    required.add_argument(
        "--name",
        metavar="name",
        type=str,
        help="The name you want to give to this experiment.",
        required=True,
    )
    optional.add_argument(
        "--characterize",
        metavar="characterize",
        type=str_to_bool,
        default=False,
        nargs="?",
        const=True,
        help="True iff you want the tool to tell you if the results are "
        + "A-, E-, or not attackers at all.  May substantially add to "
        + "runtime!",
        required=False,
    )
    required.add_argument(
        "--dir",
        metavar="dir",
        type=str,
        help="The path to the directory that contains your models, directory "
        + "MUST contain P.pml, Q.pml, Phi.pml, IO.txt.",
        required=False,
    )

    return parser
