/* spin -t4 -s -r experiment2_5_False_daisy_check.pml */
active proctype attacker() {
	
	NtoA ! ACK;
	NtoB ! ACK;
	// Acceptance Cycle part of attack
	do
	::
	   BtoN ? SYN;
	od
}