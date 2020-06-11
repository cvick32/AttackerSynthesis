from helpers import get_IO, file_read, inner_contents

class Problem:
    """
    A Problem is the given input to Korg. It gives the given 
    protocol, network, Phi, and IO a structure that allows us
    to think about the Problem as a whole more clearly. It also
    saves us a bunch of typing overhead. 
    """

    def __init__(self, P, Q, IO, phi, max_attacks, characterize_huh, recovery_huh, name):
        self.P = P
        self.Q = Q
        self.IO = get_IO(IO)
        self.phi = phi
        self.max_attacks = max_attacks
        self.characterize_huh = characterize_huh
        self.recovery_huh = recovery_huh
        self.name = name
        self.daisy_name = "daisy.pml"

    def make_daisy(self):
        '''
	    Scan the model for all send and receive events,
	    and their complements. Effectively, this is all 
	    the send and receive events possible according to
	    the (I/O) interface of the model.
	    @param events: the IO interface of the network
	    @param N:      model of the network
	    @param with_recovery: do we want with_recovery attacks?
        '''
        assert(len(self.IO) != 0)
        network = inner_contents(file_read(self.Q))

        if self.recovery_huh and (network in { False, None } or len(network.strip()) == 0):
            return None

        recovery_bitflag = "b"
        j = 0
        while "bit " + recovery_bitflag in network:
            recovery_bitflag = "b" + str(j)
            j += 1
            
        return network, recovery_bitflag