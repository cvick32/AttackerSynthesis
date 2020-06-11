c_code {
\#include "chordbase.c"
}

ltl valid {
	always ( now.succ, now.prdc, now.succ2 )
}
// still need to find out what 'now' is