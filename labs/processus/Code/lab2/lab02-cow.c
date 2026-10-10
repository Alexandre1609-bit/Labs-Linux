#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

#define SIZE (100 * 1024 * 1024)

int main(void) {
    char *memory = malloc(SIZE);

    if (memory == NULL) {
        perror("malloc");
        return 1;
    }

    for (size_t i = 0; i < SIZE; i += 4096) {
        memory[i] = 1;
    }

    printf("Avant fork : PID=%d\n", getpid());
    fflush(stdout);

    pid_t pid = fork();

    if (pid < 0) {
        perror("fork");
        free(memory);
        return 1;
    }

    if (pid == 0) {
        printf("Enfant : PID=%d\n", getpid());
        sleep(30);
        memory[0] = 2;
    } else {
        printf("Parent : PID=%d, enfant=%d\n", getpid(), pid);
        sleep(30);
        wait(NULL);
        printf("Parent : memory[0]=%d\n", memory[0]);
    }

    free(memory);
    return 0;
}