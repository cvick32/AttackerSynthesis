import os
from glob import glob

ATTACKER_FILE_PATH = "attacks/"

def make_attackers(trails, trail_cmds, problem):
    attackers = list()
    for i in range(len(trails)):
        a = Attacker(
            trails[i], trail_cmds[i], problem.get_network(), problem.recovery_huh, i
        )
        a.generate_attacker_string()
        attackers.append(a)
    return attackers

def write_attackers(attackers):
    if not os.path.isdir(ATTACKER_FILE_PATH):
        os.mkdir(ATTACKER_FILE_PATH)
    for attacker in attackers:
        attacker.write_attacker_to_file()

'''
def characterize_attacks(model, phi, with_recovery=True):
    nE, nA = 0, 0
    with open("out/log.txt", "w") as log:
        log.write("model,A/E, with_recovery?\n")
        for attackModel in glob(ATTACKER_FILE_PATH + "/attacker*.pml"):
            # is it a forall attack?
            attackName = os.path.basename(attackModel).replace(".pml", "")
            aName = "out/" + name + "/artifacts/" + attackName + "_A.pml"
            eName = "out/" + name + "/artifacts/" + attackName + "_E.pml"
            A = models(model, "negated.pml", attackModel, aName) == True
            E = models(model, phi, attackModel, eName) == False
            if A:
                nA += 1
            elif E:
                nE += 1
            log.write(
                ",".join([attackModel, attackType(A, E), str(with_recovery)]) + "\n"
            )
    return (nE, nA)
'''

class Attacker:
    def __init__(self, events, cmd, net, recovery_huh, n):
        self.acyclic_events, self.cyclic_events = events[0], events[1]
        self.acyclic_events = (
            self.acyclic_events if len(self.acyclic_events) > 0 else ["skip"]
        )
        self.cmd = cmd
        self.net = net
        self.recovery_huh = recovery_huh
        self.num_attack = n
        self.promela_code = "active proctype attacker() {\n\t"

    def generate_attacker_string(self):
        """
        Create the attacker string given the events that the 
        daisy made. This method also writes the string to a 
        file provided one doesn't already exist.
        """
        for ae in self.acyclic_events:
            self.promela_code += "\n\t" + ae + ";"

        if self.recovery_huh:
            self.promela_code += (
                "\n// recovery to N\n// N begins here ... \n" + self.net + "\n}"
            )
        else:
            self.promela_code += "\n\t// Acceptance Cycle part of attack"
            if len(self.cyclic_events) > 0:
                self.promela_code += (
                    "\n\tdo\n\t::"
                    + "".join(["\n\t   " + ce + ";" for ce in self.cyclic_events])
                    + "\n\tod"
                )
            self.promela_code += "\n}"

    def write_attacker_to_file(self):
        attacker_name = ATTACKER_FILE_PATH + self.generate_attacker_name()
        if not os.path.exists(attacker_name):
            with open(attacker_name, "w") as fw:
                fw.write(
                    "/* spin command to generate : " + " ".join(self.cmd) + " */\n"
                )
                fw.write(self.promela_code)

    def generate_attacker_name(self):
        if self.recovery_huh:
            return "attacker_" + str(self.num_attack) + "_WITH_RECOVERY" + ".pml"
        else:
            return "attacker_" + str(self.num_attack) + "_NO_RECOVERY" + ".pml"
