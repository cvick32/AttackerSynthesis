/* ========================================================================
A MODEL OF THE FULL CHORD ROUTING PROTOCOL IN PROMELA AND C
   Pamela Zave
      Copyright AT&T Labs, Inc., 2012, 2013.
======================================================================== */
/* ========================================================================
This is a model of the "best" protocol as defined in the CCR paper.  It is
derived from pseudocode and text in the Chord papers, as well as other
obvious fixes.  It is not correct.

The atomicity of the join attempt is not implementable, but it does not
matter.  In the worst case, a join fails when a member has acquired no data
and other members have acquired no pointers to it.  In this situation, the
new member can retry the join without repercussions.
======================================================================== */

#define S 4

c_code {
\#include "chordbestccr.c"
}

int succ[S] = 9;
int prdc[S] = 9;
int succ2[S] = 9;
int x, y, z;                     /* used for passing arguments to C code */

inline joinAttempt(j,m) {        /* assumes j is not a member and j != m */
   if
   :: succ[m] != 9 ->                              /* m must be a member */
      x = m; y = j; z = succ[m];        /* checking between(m,j,succ[m]) */
      if
      :: c_expr{ between(now.x, now.y, now.z) } && succ[succ[m]] != 9 -> 
         succ[j] = succ[m];
         succ2[j] = succ[succ[m]];
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: else
      fi
   :: else
   fi
}

inline stabilize(s) {                           /* assumes s is a member */
int newSucc;
   newSucc = prdc[succ[s]];

atomic {
   if
   :: newSucc != 9 ->           /* s's successor must have a predecessor */
      if
      :: succ[newSucc] != 9 ->           /* predecessor must be a member */
         x = s; y = newSucc; z = succ[s];
         if                 /* checking between(s,prdc[succ[s]],succ[s]) */
         :: c_expr { between(now.x, now.y, now.z) } ->
            succ[s] = newSucc;
            if 
            :: succ2[s] != succ[newSucc] -> succ2[s] = succ[newSucc];
            :: else
            fi;
            assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
         :: else
         fi
      :: else
      fi
   :: else
   fi;
} /* end atomic */
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
      if 
      :: succ[succ[u]] != 9 && succ2[u] != succ[succ[u]] -> 
         succ2[u] = succ[succ[u]]
      :: else
      fi;
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

   if /* there must be an initial member; 2 is an "arbitrary" choice */
   :: n == 2 ->
      succ[n] = 2; assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
   :: else
   fi;

   do
   :: succ[n] == 9 && n != 0 -> atomic { joinAttempt(n,0) }
   :: succ[n] == 9 && n != 1 -> atomic { joinAttempt(n,1) }
   :: succ[n] == 9 && n != 2 -> atomic { joinAttempt(n,2) }
   :: succ[n] == 9 && n != 3 -> atomic { joinAttempt(n,3) }
   :: succ[n] != 9 -> stabilize(n);                    
                      atomic { notified(succ[n],n) } 
   :: succ[n] != 9 -> atomic { failAttempt(n) }
       /* can fail if and only if no node is left with no live successor */
   :: succ[n] != 9 -> atomic { reconcile(n) } 
   :: succ[n] != 9 -> atomic { update(n) }  
   :: succ[n] != 9 -> atomic { flush(n) } 
   od;
}

init { atomic { run node(0);
                run node(1);
                run node(2);
                run node(3)
              } }

/* ========================================================================
======================================================================== */
