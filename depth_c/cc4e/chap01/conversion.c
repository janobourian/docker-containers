#include "stdio.h"

#define LOWER 32
#define UPPER 1000
#define STEP 10

int main(){
    float fahr;
    fahr = LOWER;

    while(fahr <= UPPER){
        printf("%5.0f %9.1f\n", fahr, (5.0/9.0) * (fahr - 32.0));
        fahr = fahr + STEP; 
    }

    return 0;
}