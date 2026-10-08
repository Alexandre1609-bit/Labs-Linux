#include <stdio.h>
#include <unistd.h>

int main(void) {
    int x = 42;

    printf("Avant fork : PID=%d, x=%d\n", getpid(), x);

    fork();

    printf("Après fork : PID=%d, PPID=%d, x=%d\n",
           getpid(), getppid(), x);

    return 0;
}
