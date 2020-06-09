#include <stdio.h>

#define S 3

int between(int x,int y,int z) {
   if (x < z) { if (x<y && y<z) return 1; }
   else       { if (x<y || y<z) return 1; }
   return 0;
}

int canFailNow(int n, int succ[S], int prdc[S], int succ2[S]) {
   int i; 
   for (i = 0; i < S; i++) { // cannot fail if fully-updated member left
      if (succ[i] == n) {    // with no live successor
         if (succ2[i] == n) return 0;
         if (succ2[i] != 9 && succ[succ2[i]] == 9) return 0;
      }
      if (succ2[i] == n) {
         if (succ[i] != 9 && succ[succ[i]] == 9) return 0;
      }
   }
   return 1;                         
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

int ringSize(int reach[S][S]) {
   int i, k;
   k = 0;
   for (i = 0; i < S; i++) {
      if (reach[i][i] == 1) k++;
   }
   return k;
}

int reconciled(int succ[S], int succ2[S]) { // succ2's are correct
   int i;
   for (i = 0; i < S; i++) {
      if (succ[i] != 9 && succ2[i] != succ[succ[i]]) return 0;
   }
   return 1;
}

int hasbest(int succ[S], int succs[S][S]) { // members have live successors
   int i;
   for (i = 0; i < S; i++) {
      if (succ[i] != 9 && succs[i][0] == 9) return 0;
   }
   return 1;
}

int alor(int reach[S][S]) { // At Least One Ring
   int i;
   for (i = 0; i < S; i++) {
      if (reach[i][i] == 1) return 1;
   }
   return 0;
}

int amor(int reach[S][S]) { // At Most One Ring
   int i, j;
   for (i = 0; i < S; i++) {
      for (j = i+1; j < S; j++) {
         if (reach[i][i] == 1 && reach[j][j] == 1) {
            if (reach[i][j] == 0) return 0;
            if (reach[j][i] == 0) return 0;
         }
      }
   }
   return 1;
}

int ordring(int succs[S][S], int reach [S][S]) { // Ordered Ring
   int i, j, k;
   for (i = 0; i < S; i++) {
      if (reach[i][i] == 1) {
         j = succs[i][0];
         for (k = 0; k < S; k++) {
            if (k != i && k != j && reach[k][k] == 1 && between(i,k,j)) 
               return 0;
         }
      }
   }
   return 1;
}

int connapp(int succs[S][S], int reach [S][S]) { // Connected Appendages
   int i, j, k;
   for (i = 0; i < S; i++) {
      if (succs[i][0] != 9 && reach[i][i] == 0) { // i in appendage
         for (j = 0; j < S; j++) {
            k = succs[i][j];
            if (k == 9) return 0;
            if (reach[k][k] == 1) break;
         }
      }
   }
   return 1;
}

int allring(int succs[S][S], int reach [S][S]) { 
   int i;
   for (i = 0; i < S; i++) {
      if (succs[i][0] != 9 && reach[i][i] != 1) return 0;
   }
   return 1;
}

int stable(int succ [S], int prdc [S]) {
   int i, j;
   for (i = 0; i < S; i++) {
      if (succ[i] != 9) {
         if (prdc[succ[i]] != i) return 0;
      }
   }
   for (i = 0; i < S; i++) {
      if (prdc[i] != 9) {
         if (succ[prdc[i]] != i) return 0;
      }
   }
   return 1;
}

int populateMatrices
   (int succ[S],int prdc[S],int succ2[S],int succs[S][S],int reach[S][S]) {
   int i, j, k; 
// initialize succs[i][0] to bestsucc[i], reach[i][j] to false
   for (i = 0; i < S; i++) {
      if (succ[succ[i]] != 9) // succ[i] is live
         succs[i][0] = succ[i];
      else if (succ[succ2[i]] != 9) // succ2[i] is live
         succs[i][0] = succ2[i];
      else 
         succs[i][0] = 9;
      reach[i][0] = 0;
   }
   for (i = 0; i < S; i++) {
      for (j = 1; j < S; j++) {
         succs[i][j] = 9;
         reach[i][j] = 0;
      }
   }
// populate succs with subsequent best successors
   for (j = 0; j < S-1; j++) {
      for (i = 0; i < S; i++) {
         k = succs[i][j];
         if (k == 9) 
              succs[i][j+1] = 9; 
         else succs[i][j+1] = succs[k][0];
      }
   }
// populate reach with true where reachable
   for (i = 0; i < S; i++) {
      for (j = 0; j < S; j++) {
         k = succs[i][j];
         if (k != 9) reach[i][k] = 1;
      }
   }
}

int printState( int succ[S], int prdc[S], int succ2[S] ) {
   int i;
   Printf("succ    ");
   for (i = 0; i < S; i++) {
      Printf("%d: %d   ",i,succ[i]);
   }
   Printf("\nsucc2   ");
   for (i = 0; i < S; i++) {
      Printf("%d: %d   ",i,succ2[i]);
   }
   Printf("\nprdc    ");
   for (i = 0; i < S; i++) {
      Printf("%d: %d   ",i,prdc[i]);
   }
   Printf("\n");
} 

int printMatrices(int succs[S][S], int reach[S][S]) {
int i, j;
   for (i = 0; i < S; i++) {
      Printf("%d: ",i);
      for (j = 0; j < S; j++) {
         Printf("%d ",succs[i][j]);
      };
      Printf("\n");
   }
   Printf("\n");
   for (i = 0; i < S; i++) {
      Printf("   ");
      for (j = 0; j < S; j++) {
         Printf("%d ",reach[i][j]);
      };
      Printf("\n");
   }
}

int valid(int succ[S], int prdc[S], int succ2[S]) {
   int succs[S][S]; 
   int reach[S][S];
   populateMatrices(succ,prdc,succ2,succs,reach);

   if   (hasbest(succ,succs) && alor(reach) && amor(reach) && 
         ordring(succs,reach) && connapp(succs,reach)) return 1;
   else {  printState(succ,prdc,succ2);
           printMatrices(succs,reach); 
           return 0; }
}

int ideal(int succ[S], int prdc[S], int succ2[S]) {
   int succs[S][S]; 
   int reach[S][S];
   populateMatrices(succ,prdc,succ2,succs,reach);

   if (hasbest(succ,succs) && alor(reach) && amor(reach) && 
         ordring(succs,reach) && connapp(succs,reach)) { // valid
      if (allring(succs,reach) && stable(succ,prdc) && 
            reconciled(succ,succ2)) return 1;
      else return 0;
   }
   else return 0;
}

