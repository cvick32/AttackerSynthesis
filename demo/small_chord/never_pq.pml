never  {    /* (<> [] churnStopped) && ! (<> [] perfect) */
T0_init:
	do
	:: (! ((perfect)) && (churnStopped)) -> goto accept_S90
	:: ((churnStopped)) -> goto T0_S90
	:: (1) -> goto T0_init
	od;
accept_S90:
	do
	:: ((churnStopped)) -> goto T0_S90
	od;
T0_S90:
	do
	:: (! ((perfect)) && (churnStopped)) -> goto accept_S90
	:: ((churnStopped)) -> goto T0_S90
	od;
}
