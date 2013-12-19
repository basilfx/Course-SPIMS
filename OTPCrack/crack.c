#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>

#define THREAD_COUNT 8
#define SWAP(x, y) (x=(x ^ y), y=(x ^ y), x=(x ^ y))

extern void md5_compress(uint32_t *state, uint32_t *block);

void md5_hash(uint8_t *message, uint32_t *hash) {
    hash[0] = UINT32_C(0x67452301);
    hash[1] = UINT32_C(0xEFCDAB89);
    hash[2] = UINT32_C(0x98BADCFE);
    hash[3] = UINT32_C(0x10325476);

    int i = 0;
    //for (i = 0; i + 64 <= 16; i += 64)
    md5_compress(hash, (uint32_t*)(message + i));

    uint32_t block[16];
    uint8_t *byteBlock = (uint8_t*)block;

    int rem = 16 - i;
    memcpy(byteBlock, message + i, rem);

    byteBlock[rem] = 0x80;
    rem++;
    if (64 - rem >= 8)
        memset(byteBlock + rem, 0, 56 - rem);
    else {
        memset(byteBlock + rem, 0, 64 - rem);
        md5_compress(hash, block);
        memset(block, 0, 56);
    }
    block[14] = 16 << 3;
    block[15] = 16 >> 29;
    md5_compress(hash, block);
}

typedef struct {
    uint8_t index;
    float target;
    double start;
    double end;
    int r_start;
    int r_step;
} t_arguments ;

void *bruteforce1(void *data) {
    t_arguments* arguments = (t_arguments *)data;
    printf("Thread with start=%.52f end=%.52f target=%.52f\r\n", arguments->start, arguments->end, arguments->target);

    //double start = arguments->start;
    double end = arguments->end;
    double target = arguments->target;

    double value;
    double next = end;
    uint32_t i = 0;

    uint64_t* p = (uint64_t*)&next;

    while (i < 100) {
        value = next * target;

        printf("%.55f\n", next);

        // Increment
        --*p;
        i++;
    }

    value = value + 1;

    return NULL;
}

static uint32_t h[16] = { 239, 117, 58, 70, 46, 135, 146, 75, 37, 194, 232, 173, 218, 8, 143, 110 };
//static uint32_t ref[16] = { 177, 28, 139, 208, 155, 92, 86, 180, 249, 16, 2, 171, 22, 251, 248, 100 };
static uint32_t k[4] =  {3498777777, 3025558683, 2869039353, 1694038806};
static uint8_t t[] = "AABBCCDDEEFFGGHH";

void *bruteforce(void *data) {
    t_arguments* arguments = (t_arguments *)data;

    uint8_t r[16];
    uint32_t d[4];

    r[2] = '.';

    int r_count = 0;
    int r_index = arguments->index;
    int r_start = arguments->r_start;
    int r_step = arguments->r_step;

    for (r[0] = '7'; r[0] <= '9'; r[0]++) {
        for (r[1] = '1'; r[1] <= '9'; r[1]++) {
        //for (r[2] = '1'; r[2] <= '9'; r[2]++) {
            for (r[3] = '0'; r[3] <= '9'; r[3]++) {
                for (r[4] = '0'; r[4] <= '9'; r[4]++) {
                    for (r[5] = '0'; r[5] <= '9'; r[5]++) {
                        for (r[6] = '0'; r[6] <= '9'; r[6]++) {
                            for (r[7] = '0'; r[7] <= '9'; r[7]++) {
                                printf("Thread %d: %d\n", r_index, r_count++);

                                for (r[8] = '0' + r_start; r[8] <= '9'; r[8] = r[8] + r_step) {
                                    for (r[9] = '0'; r[9] <= '9'; r[9]++) {
                                        for (r[10] = '0'; r[10] <= '9'; r[10]++) {
                                            for (r[11] = '0'; r[11] <= '9'; r[11]++) {
                                                for (r[12] = '0'; r[12] <= '9'; r[12]++) {
                                                    for (r[13] = '0'; r[13] <= '9'; r[13]++) {
                                                        for (r[14] = '0'; r[14] <= '9'; r[14]++) {
                                                            for (r[15] = '0'; r[15] <= '9'; r[15]++) {
                                                                // a.bcd...z
                                                                /*md5_hash(r, d);

                                                                if (h[0] == d[0] && h[1] == d[1] && h[2] == d[2] && h[3] == d[3]) {
                                                                    printf("Found: %s", r);
                                                                    goto end;
                                                                }*/

                                                                // ab.cd...z
                                                                //SWAP(r[1], r[2]);
                                                                md5_hash(r, d);

                                                                if (h[0] == d[0] && h[1] == d[1] && h[2] == d[2] && h[3] == d[3]) {
                                                                    printf("Found: %s", r);
                                                                    goto end;
                                                                }

                                                                // abc.d...z
                                                                //SWAP(r[2], r[3]);
                                                                /*md5_hash(r, d);

                                                                if (h[0] == d[0] && h[1] == d[1] && h[2] == d[2] && h[3] == d[3]) {
                                                                    printf("Found: %s", r);
                                                                    goto end;
                                                                }*/

                                                                //a.bcd..z
                                                                //SWAP(r[3], r[2]);
                                                                //SWAP(r[2], r[1]);
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    end:
    return NULL;
}

void test() {
    uint32_t d[4];
    md5_hash(t, d);

    if (k[0] == d[0] && k[1] == d[1] && k[2] == d[2] && k[3] == d[3]) {
        printf("MD5 OK\r\n");
    }
}

int main(void) {
    t_arguments arguments[THREAD_COUNT];
    pthread_t thread_info[THREAD_COUNT];
    uint8_t i;

    test();

    for (i = 0; i < THREAD_COUNT; i++) {
        arguments[i].index = i;
        arguments[i].target = 245.28983;
        arguments[i].start = 0;
        arguments[i].end = 1.0;
        arguments[i].r_start = i;
        arguments[i].r_step = THREAD_COUNT;

        pthread_create(&thread_info[i], NULL, bruteforce, &arguments[i]);
    }

    for (i = 0; i < THREAD_COUNT; i++) {
        pthread_join(thread_info[i], NULL);
    }

    return 0;
}