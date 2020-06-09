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
\#include "chord_incorrect.c"
}

int nonMember = 9; // arbitrary int standing in as non-member-ness

// initialize everything has nonMembers
int succ[S] = nonMember; 
int prdc[S] = nonMember;
int succ2[S] = nonMember;
int x, y, z;                     /* used for passing arguments to C code */

inline joinAttempt(j,m) {        /* assumes j is not a member and j != m */
   if
   :: succ[m] != nonMember ->                              /* m must be a member */
      x = m; y = j; z = succ[m];        /* checking between(m,j,succ[m])  makes sure that the joining node is between the current node and its successor*/ 
      if
      :: c_expr{ between(now.x, now.y, now.z) } && succ[succ[m]] != nonMember -> // succ[succ[m]] != nonMember means the successor of m's successor is a member
         succ[j] = succ[m];
         succ2[j] = succ[succ[m]];
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: else
      fi
   :: else
   fi
}

/*
"when a member stabilizes it learns its succerssor's predecessor. 
it adopts the new predecessor as its new successor, provided
that the predecessor is closer in identifier order than the current 
sucessor"
*/
inline stabilize(s) {                           /* assumes s is a member */
   int newSuccForS;
   newSuccForS = prdc[succ[s]];
   
   atomic {
      if
      :: newSuccForS != nonMember ->           /* s's successor must have a predecessor */
         if
         :: succ[newSuccForS] != nonMember ->           /* predecessor must be a member */
            x = s; y = newSuccForS; z = succ[s];
            if                 /* checking between(s,prdc[succ[s]],succ[s]) */
            :: c_expr { between(now.x, now.y, now.z) } ->
               succ[s] = newSuccForS;
               if 
               :: succ2[s] != succ[newSuccForS] -> succ2[s] = succ[newSuccForS];
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
   :: succ[t] != nonMember ->                     /* notified t must be a member */
      if
      :: prdc[t] == nonMember -> 
         prdc[t] = p;
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: prdc[t] != nonMember ->
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
      succ[f] = nonMember; prdc[f] = nonMember; succ2[f] = nonMember;
      assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
   :: else
   fi
}

inline reconcile(r) {                          
   if
   :: succ[r] != nonMember ->                              /* r must be a member */
      if 
      :: succ[succ[r]] != nonMember && succ2[r] != succ[succ[r]] -> 
         succ2[r] = succ[succ[r]];
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: else
      fi
   :: else
   fi
}

inline update(u) {                              /* assumes u is a member */
   if
   :: succ[succ[u]] == nonMember && succ2[u] != nonMember -> 
      succ[u] = succ2[u]; succ2[u] = nonMember;
      if 
      :: succ[succ[u]] != nonMember && succ2[u] != succ[succ[u]] -> 
         succ2[u] = succ[succ[u]]
      :: else
      fi;
      assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
   :: else
   fi
}

inline flush(f) { 
   if 
   :: prdc[f] != nonMember ->                       /* f must have a predecessor */
      if
      :: succ[prdc[f]] == nonMember -> 
         prdc[f] = nonMember;
         assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
      :: else
      fi
   :: else
   fi
}

proctype node (byte n) {

   if /* there must be an initial member; 1 is an "arbitrary" choice */
   :: n == 1 ->
      succ[n] = 1; assert c_expr{ valid( now.succ, now.prdc, now.succ2) }
   :: else
   fi;

   do
   :: succ[n] == nonMember && n != 0 -> atomic { joinAttempt(n,0) }
   :: succ[n] == nonMember && n != 1 -> atomic { joinAttempt(n,1) }
   :: succ[n] == nonMember && n != 2 -> atomic { joinAttempt(n,2) }
   :: succ[n] == nonMember && n != 3 -> atomic { joinAttempt(n,3) }
   :: succ[n] != nonMember -> stabilize(n);                    
                      atomic { notified(succ[n],n) } 
   :: succ[n] != nonMember -> atomic { failAttempt(n) }
       /* can fail if and only if no node is left with no live successor */
   :: succ[n] != nonMember -> atomic { reconcile(n) } 
   :: succ[n] != nonMember -> atomic { update(n) }  
   :: succ[n] != nonMember -> atomic { flush(n) } 
   od;
}

init { atomic { run node(0);
                run node(1);
                run node(2);
                run node(3);
              } }

/* ========================================================================
======================================================================== */
