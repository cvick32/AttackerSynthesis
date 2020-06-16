from problem import Problem
from glob import glob
from cli import parse_args, clean_and_exit
from helpers import coalesce, clean_up
from spin import run_spin, make_all_trails, generate_trail_commands, parse_all_trails
from attacker import Attacker, make_attackers, write_attackers


def solve_attacker_syn(p):
    """
	Attempts to solve the attacker synthesis problem given the problem definition
	find attackers against a given model. The attacker 
	is successful if the given phi is violated. The phi is initially 
	evaluated by being composed with Q. 
	@param p.P            : a promela model 
	@param p.phi          : LTL property satisfied by model || Q
	@param p.Q            : a promela model
	@param p.IO           : Input Output interface of Q's communication channels
	@param p.max_attacks  : how many attackers to generate
	@param p.recovery_huh : should the attackers recover?
	@param p.name         : name of the files
	@param p.characterize_huh : do you want us to characterize attackers after 
						  producing them?
	"""
    p.make_daisy()
    p.write_daisy()
    p.make_phi()

    problem_file = coalesce([p.P, p.phi, p.daisy_name], p.daisy_models_name)

    if not run_spin(problem_file):
        p.print_no_solution()
        clean_and_exit()

    make_all_trails(problem_file, p.max_attacks)
    trail_cmds = generate_trail_commands(p.daisy_models_name)
    trails = parse_all_trails(trail_cmds, p.recovery_huh)
    attackers = make_attackers(trails, trail_cmds, p)

    write_attackers(attackers)
    clean_up()
    '''
    # Characterize the attacks
    if p.characterize_huh:
        (E, A) = characterizeAttacks(model, phi, with_recovery, attacker_name)
        clean_up()
        return 0 if (E + A) > 0 else -1
    else:
        '''
        
    return 0  # assume it worked if not asked to prove it ...


if __name__ == "__main__":
    problem = parse_args()
    solve_attacker_syn(problem)
