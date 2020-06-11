from problem import Problem
from glob import glob
from cli import parse_args

"""

"""


def main():
    problem = parse_args()
    return solve(problem)


def solve(p):
    """
	Attempts to solve the attacker synthesis problem given the problem definition
	find attackers against a given model. The attacker 
	is successful if the given phi is violated. The phi is initially 
	evaluated by being composed with Q. 
	@param p.P        : a promela model 
	@param p.phi          : LTL property satisfied by model || Q
	@param p.Q            : a promela model
	@param p.IO           : Input Output interface of Q's communication channels
	@param p.max_attacks  : how many attackers to generate
	@param p.recovery_huh : should the attackers be with_recovery?
	@param p.name         : name of the files
	@param p.characterize_huh : do you want us to characterize attackers after 
						  producing them?
	"""

    # The name of the file we use to check that (model, (Q), phi) has a
    # with_recovery attacker
    with_recovery_phi_name = p.name + "_with_recovery_phi.pml"
    # The subdirectory of out/ where we write our results
    attacker_name = p.name + "_" + str(p.recovery_huh)
    # The name of the file we use to check that model || daisy(Q) |/= phi
    daisy_models_name = p.name + "_daisy_check.pml"

    p.IO = sorted(list(p.IO))  # sorted list of events
    # Make daisy attacker
    net, label = makeDaisy(IO, Q, with_recovery, daisy_name)
    daisy_string = makeDaisyWithEvents(IO, with_recovery, net, label)
    writeDaisyToFile(daisy_string, daisy_name)

    if with_recovery == False:
        daisyPhi = phi
    else:
        daisyPhiString = makeDaisyPhiFinite(label, phi)
        with open(with_recovery_phi_name, "w") as fw:
            fw.write(daisyPhiString)
        daisyPhi = with_recovery_phi_name

    # model, phi, N, name
    _models = models(model, daisyPhi, daisy_name, daisy_models_name)

    if net == None or _models:
        printNoSolution(model, phi, Q, with_recovery)
        cleanUp()
        return 6

    makeAllTrails(daisy_models_name, max_attacks)
    # second arg is max# attacks to make

    cmds = trailParseCMDs(daisy_models_name)
    attacks, provenance = parseAllTrails(cmds, with_recovery)

    # Write these attacks to models
    writeAttacks(attacks, provenance, net, with_recovery, attacker_name)

    # Characterize the attacks
    if characterize:
        (E, A) = characterizeAttacks(model, phi, with_recovery, attacker_name)
        cleanUp()
        return 0 if (E + A) > 0 else -1
    else:
        cleanUp()
        return 0  # assume it worked if not asked to prove it ...


if __name__ == "__main__":
    main()
