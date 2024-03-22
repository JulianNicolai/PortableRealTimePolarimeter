#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <math.h>

struct complex {
    float real;
    float imag;
};

struct complex goertzel_mag(uint16_t* data, uint32_t numSamples, uint16_t target_freq) {
    float omega, sine, cosine, coeff, q0, q1, q2;
    
    struct complex value;

    float scalingFactor = 2.0 / (numSamples * 65535.0);

    omega = 2.0 * M_PI * target_freq / numSamples;
    sine = sin(omega);
    cosine = cos(omega);
    coeff = 2.0 * cosine;
    q0 = 0.0;
    q1 = 0.0;
    q2 = 0.0;

    for (uint32_t i = 0; i < numSamples; i++) {
        q0 = coeff * q1 - q2 + data[i];
        q2 = q1;
        q1 = q0;
    }

    value.real = (q1 - q2 * cosine) * scalingFactor;
    value.imag = (q2 * sine) * scalingFactor;

    return value;
}

struct complex goertzel_mag0(uint16_t* data, uint32_t numSamples) {
    struct complex value;
    float total = 0.0;
    for (int i = 0; i < numSamples; i++) {
        total = total + data[i];
    }
    value.real = total / (numSamples * 65535.0);
    value.imag = 0.0;
    return value;
}

void load_data(uint16_t *data) {
    FILE *file = fopen("test_data2.csv", "r");
    
    int i = 0;
    int num;
    while(fscanf(file, "%d", &num) == 1) {
        data[i] = num;
        i++;
    }
    fclose(file);
}

void print_complex(struct complex value) {
    if (value.imag >= 0) {
        printf("%.4f + i%.4f", value.real, fabs(value.imag));
    } else {
        printf("%.4f - i%.4f", value.real, fabs(value.imag));
    }
}

int main() {

    int samples = 12968;
    uint16_t data[100000];

    load_data(data);
    printf("Loaded data!\n");

    uint8_t cycles = 5;
    uint16_t w0 = 0;
    uint16_t w1 = cycles * 2;
    uint16_t w2 = cycles * 4;

    struct complex res0 = goertzel_mag0(data, samples);
    struct complex res1 = goertzel_mag(data, samples, w1);
    struct complex res2 = goertzel_mag(data, samples, w2);

    print_complex(res0);
    printf(" == 0.2626 + i0.0000\n");
    print_complex(res1);
    printf(" == -0.0051 - i0.1139\n");
    print_complex(res2);
    printf(" == -0.2355 + i0.0542\n");

    // uint16_t freqCutoff = 200;
    // for (uint16_t w = 0; w < freqCutoff; w++) {
    //     struct complex res = goertzel_mag(data, samples, w, cycles);
    //     // print_complex(res);
    //     printf("%.10f\n", sqrtf(res.real * res.real + res.imag * res.imag));
    //     // printf("%u rad/s: %.5f\n", w, sqrtf(res.real * res.real + res.imag * res.imag));
    // }
    
    return 0;
}