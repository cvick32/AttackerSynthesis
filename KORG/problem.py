from helpers import get_IO, file_read, inner_contents, file_write


class Problem:
    """
    A Problem is the given input to Korg. It gives the given 
    protocol, network, Phi, and IO a structure that allows us
    to think about the Problem as a whole more clearly. It also
    saves us a bunch of typing overhead. 
    """

    def __init__(
        self, P, Q, IO, phi, max_attacks, characterize_huh, recovery_huh, name
    ):
        self.P = P
        self.Q = Q
        self.IO = sorted(list(get_IO(IO)))
        self.phi = phi  # string to path to the phi file
        self.max_attacks = max_attacks
        self.characterize_huh = characterize_huh
        self.recovery_huh = recovery_huh
        self.name = name
        self.daisy_name = "daisy.pml"

        # The name of the file we use to check that (model, (Q), phi) has a with_recovery attacker
        self.daisy_models_name = name + "_daisy_check.pml"
        # The subdirectory of out/ where we write our results
        self.attacker_name = name + "_" + str(recovery_huh)

    def make_daisy(self):
        """
	    Scan the model for all send and receive events,
	    and their complements. Effectively, this is all 
	    the send and receive events possible according to
	    the (I/O) interface of the model.
        """
        network = self.get_network()
        self.recovery_bitflag = self.scan_model(network)
        daisy = "active proctype daisy () {\n\tdo"
        if self.recovery_huh:
            daisy = "bit " + self.recovery_bitflag + "= 0;\n" + daisy
        for event in self.IO:
            daisy += "\n\t:: " + event
        if self.recovery_huh:
            daisy += "\n\t:: break; // recovery to N ... \n\tod"
            daisy += "\n\t" + self.recovery_bitflag + " = 1;\n\t"
            # Add recovery to N
            daisy += "// N begins here ... \n" + network + "\n}"
        else:
            daisy += "\n\tod\n}"
        self.daisy = daisy

    def scan_model(self, network):
        """
        This is a hold-over from the old code, still not quite sure 
        what it does
        """
        if self.recovery_huh and (
            network in {False, None} or len(network.strip()) == 0
        ):
            return None
        recovery_bitflag = "b"
        j = 0
        while "bit " + recovery_bitflag in network:
            recovery_bitflag = "b" + str(j)
            j += 1
        return recovery_bitflag

    def write_daisy(self):
        file_write(self.daisy_name, self.daisy)

    def make_phi(self):
        """
        If we want recovery, we create a new phi that recovers based
        on the recovery bitflag generated from scanning the model. 
        If not, we keep the same phi. 
	    """
        if self.recovery_huh == True:
            self.phi = (
                self.name
                + "_recovery_phi.pml"  # we now use this recovery phi as our phi
            )
            phiBody = inner_contents(file_read(self.phi))
            newPhi = (
                "ltl newPhi {\n\t(eventually ( "
                + self.recovery_bitflag
                + " == 1 ) ) implies (\n\t\t"
                + phiBody
                + "  )\n}"
            )
            file_write(self.phi, newPhi)

    def get_network(self):
        return inner_contents(file_read(self.Q))

    # Error message for if we cannot find any solution.
    def print_no_solution(self):
        possiblyFinite = "with_recovery" if self.recovery_huh else ""
        print(
            "We could not find any " + possiblyFinite + "(model, (N), phi)-attacker A."
        )
