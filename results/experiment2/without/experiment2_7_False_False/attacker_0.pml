/* spin -t0 -s -r experiment2_7_False_daisy_check.pml */
active proctype attacker() {
	
	NtoA ! ACK;
	NtoB ! ACK;
	// Acceptance Cycle part of attack
	do
	::
	   BtoN ? SYN;
	od
}