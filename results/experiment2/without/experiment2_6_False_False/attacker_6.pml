/* spin -t6 -s -r experiment2_6_False_daisy_check.pml */
active proctype attacker() {
	
	NtoA ! ACK;
	NtoB ! ACK;
	// Acceptance Cycle part of attack
	do
	::
	   BtoN ? SYN;
	   AtoN ? SYN;
	od
}