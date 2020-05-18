#include <stdio.h>

#define S 4

int between(int x,int y,int z) {
   if (x < z) { if (x<y && y<z) return 1; }
   else       { if (x<y || y<z) return 1; }
   return 0;
}

int canFailNow(int n, int succ[S], int prdc[S], int succ2[S]) {
   int i; 
   int otherLive = 0;
   for (i = 0; i < S; i++) { // cannot fail if fully-updated member left
      if (succ[i] == n) {    // with no live successor
         if (succ2[i] == n) return 0;
         if (succ2[i] != 9 && succ[succ2[i]] == 9) return 0;
      }
      if (succ2[i] == n) {
         if (succ[i] != 9 && succ[succ[i]] == 9) return 0;
      }
   }
   for (i = 0; i < S; i++) { // cannot fail if n is last member
      if (i != n && succ[i] != 9) otherLive = 1;
   }
   if (otherLive) return 1; else return 0;                        
   /*
   int succs[S][S]; 
   int reach[S][S];
   populateMatrices(succ,prdc,succ2,succs,reach);
   if (reach[n][n] == 1 && ringSize(reach) < 4) 
      return 0; // cannot fail if ring left at 2 or smaller
   */
}

int canJoinNow(int n, int succ[S], int prdc[S], int succ2[S]) {
   return 1;
}

/*
int canJoinNow(int n, int succ[S], int prdc[S], int succ2[S]) {
   int i; // cannot join if there are obsolete pointers to joiner
   for (i = 0; i < S; i++) {
      if (succ[i] == n) return 0;
      if (prdc[i] == n) return 0;
      if (succ2[i] == n) return 0;
   }
   return 1;
}
*/