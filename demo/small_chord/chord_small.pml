/* ========================================================================
A MODEL OF THE FULL CHORD ROUTING PROTOCOL IN PROMELA AND C
   Pamela Zave
      Copyright AT&T Labs, Inc., 2012.
======================================================================== */
/* ========================================================================
This is a model of a correct version of Chord, with a permanent base set of
members of size n+1, where n is the length of the successor list.
======================================================================== */

#define S 3

c_code {
\#include "chordbase.c"
}

int succ[S] = 9;
int prdc[S] = 9;
int succ2[S] = 9;
int newSucc[S] = 9;    /* used to communicate data between inline macros */
int x, y, z;                     /* used for passing arguments to C code */

bool churn = false; // used for ltl

inline joinCheck(j,m) {          /* assumes j is not a member and j != m */
   newSucc[j] = succ[m];
}

inline join(j,m) {               /* assumes j is not a member and j != m */
   if
   :: newSucc[j] != 9 ->                           /* m must be a member */
      if
      :: succ[newSucc[j]] != 9 ->      /* m's successor must be a member */
         x = m; y = j; z = newSucc[j];  /* checking between(m,j,succ[m]) */
         if
         :: c_expr{ between(now.x, now.y, now.z) } ->
            if
            :: c_expr { canJoinNow(now.y,now.succ,now.prdc,now.succ2) } -> 
               succ[j] = newSucc[j]; 
               assert c_expr{ valid( now.succ, now.prdc, now.succ2) };
            :: else 
            fi
         :: else 
         fi
      :: else 
      fi;
      newSucc[j] = 9
   :: else
   fi
}

inline stabilizeCheck(s) {                      /* assumes s is a member */
   newSucc[s] = prdc[succ[s]]
}

inline stabilize(s) {                           /* assumes s is a member */
   if
   :: newSucc[s] != 9 ->        /* s's successor must have a predecessor */
      if
      :: succ[newSucc[s]] != 9 ->        /* predecessor must be a member */
         x = s; y = newSucc[s]; z = succ[s];
         if                 /* checking between(s,prdc[succ[s]],succ[s]) */
         :: c_expr { between(now.x, now.y, now.z) } ->
            succ[s] = newSucc[s];
            assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
         :: else 
         fi
      :: else
      fi;
      newSucc[s] = 9
   :: else
   fi
}

inline notified(t,p) { 
   if
   :: succ[t] != 9 ->                     /* notified t must be a member */
      if
      :: prdc[t] == 9 -> 
         prdc[t] = p;
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: prdc[t] != 9 ->
         x = prdc[t]; y = p; z = t;     /* checking between(prdc[t],p,t) */
         if
         :: c_expr{ between(now.x, now.y, now.z) } ->
            prdc[t] = p; 
            assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
         :: else
         fi
      fi
   :: else
   fi
}

inline failAttempt(f) {                         /* assumes f is a member */
   x = f;
   if
   :: c_expr { canFailNow( now.x, now.succ, now.prdc, now.succ2 ) } ->
      succ[f] = 9; prdc[f] = 9; succ2[f] = 9;
      assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
   :: else 
   fi
}

inline reconcile(r) {                          
   if
   :: succ[r] != 9 ->                              /* r must be a member */
      if 
      :: succ[succ[r]] != 9 && succ2[r] != succ[succ[r]] -> 
         succ2[r] = succ[succ[r]];
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: else
      fi
   :: else
   fi
}

inline update(u) {                              /* assumes u is a member */
   if
   :: succ[succ[u]] == 9 && succ2[u] != 9 -> 
      succ[u] = succ2[u]; succ2[u] = 9;
      assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
   :: else
   fi
}

inline flush(f) { 
   if 
   :: prdc[f] != 9 ->                       /* f must have a predecessor */
      if
      :: succ[prdc[f]] == 9 -> 
         prdc[f] = 9;
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: else
      fi
   :: else
   fi
}

proctype node (byte n) {

   do
  // :: true -> churn = true;
   :: (n == 0) && succ[n] == 9 -> 
         atomic { joinCheck(n,1); } atomic { join(n,1); reconcile(n) }
   :: (n == 0) && succ[n] == 9 -> 
         atomic { joinCheck(n,2); } atomic { join(n,2); reconcile(n) }

   :: succ[n] != 9 -> atomic { stabilizeCheck(n); }
                      atomic { stabilize(n); reconcile(n); } 
                      atomic { flush(succ[n]); notified(succ[n],n) }

   :: (n == 0) && succ[n] != 9 
         -> atomic { failAttempt(n) }

   :: succ[n] != 9 -> atomic { reconcile(n) }           
   :: succ[n] != 9 -> atomic { update(n); reconcile(n) }
   :: succ[n] != 9 -> atomic { flush(n) }  
   od;
}

init { succ[1] = 2;           /* these are permanent members of the ring */
       succ[2] = 1;
       succ2[1] = 2; 
       succ2[2] = 1; 
       atomic { run node(0);
                run node(1);
                run node(2);
              } }

/* ========================================================================
======================================================================== */
