#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <math.h>

#define ENABLE_WINDOW 0

struct DataPacket {
    char start[4];
    uint32_t samples;
    uint32_t dt;
    float S0;
    float S1;
    float S2;
    float S3;
};

struct complex {
    float real;
    float imag;
};

static const float normalisationFactor = 1 / 65535.0;
static const float M_PI2 = 2.0 * 3.14159265358979323846;

static uint32_t numSamples;
static float numSamplesI;
static float scalingFactor0;
static float scalingFactor;

static float omega1, omega2;
static float sine1, sine2;
static float cosine1, cosine2;
static float coeff1, coeff2;
static float q0_1, q0_2;
static float q1_1, q1_2;
static float q2_1, q2_2;

static uint8_t cycles = 5; 

struct complex A0, A1, A2;

static struct DataPacket packet = {{'$', '$', '$', '$'}, 0, 0, 0.0, 0.0, 0.0, 0.0};

uint16_t dataBuffer[100000];

void compute_stokes() {
    packet.S1 = A2.real * 4.0;
    packet.S2 = A2.imag * -4.0;
    packet.S3 = A1.imag * -2.0;
    packet.S0 = 2.0 * A0.real - packet.S1 * 0.5;
}

void compute_params() {
    numSamplesI = 1.0 / packet.samples;
    scalingFactor0 = numSamplesI * normalisationFactor;
    scalingFactor = 2.0 * scalingFactor0;
    omega1 = 2.0 * cycles * M_PI2 * numSamplesI;
    omega2 = 2.0 * omega1;
    sine1 = sin(omega1);
    sine2 = sin(omega2);
    cosine1 = cos(omega1);
    cosine2 = cos(omega2);
    coeff1 = 2.0 * cosine1;
    coeff2 = 2.0 * cosine2;
}

void apply_window() {
    float A = 2.0 / packet.samples;
    float B, C;
    int n = 0;
    for (n = 0; n < packet.samples; n++) {
        B = n * 2.0 * numSamplesI - 1;
        C = 1.0 - B * B;
        dataBuffer[n] = dataBuffer[n] * C * 1.5;  // 1.5 amplitude correction factor (1/mean of window function)
    }
}

void goertzel() {

    q0_1 = 0.0;
    q1_1 = 0.0;
    q2_1 = 0.0;
    
    q0_2 = 0.0;
    q1_2 = 0.0;
    q2_2 = 0.0;

    float total = 0.0;
    float value;
    float A, B;
    int i;
    for (i = 0; i < packet.samples; i++) {

        if (ENABLE_WINDOW) {
            A = i * 2.0 * numSamplesI - 1;
            B = 1.0 - A * A;
            value = (float) dataBuffer[i] * B * 1.5;  // 1.5 amplitude correction factor (1/mean of window function)
        } else {
            value = (float) dataBuffer[i];
        }

        total = total + value;

        q0_1 = coeff1 * q1_1 - q2_1 + value;
        q2_1 = q1_1;
        q1_1 = q0_1;

        q0_2 = coeff2 * q1_2 - q2_2 + value;
        q2_2 = q1_2;
        q1_2 = q0_2;
    }

    A0.real = total * scalingFactor0;
    A0.imag = 0.0;

    A1.real = (q1_1 - q2_1 * cosine1) * scalingFactor;
    A1.imag = (q2_1 * sine1) * scalingFactor;

    A2.real = (q1_2 - q2_2 * cosine2) * scalingFactor;
    A2.imag = (q2_2 * sine2) * scalingFactor;
}

void process_data() {
    compute_params();
    apply_window(); // Applies Welch window (polynomial)
    goertzel();
    compute_stokes();
}

void load_data(uint16_t *data) {
    FILE *file = fopen("test_data3.csv", "r");
    
    int i = 0;
    int num;
    while(fscanf(file, "%d", &num) == 1) {
        data[i] = num;
        i++;
    }
    fclose(file);
    printf("Loaded data!\n");
}

void print_complex(struct complex value) {
    if (value.imag >= 0) {
        printf("%.4f + i%.4f", value.real, fabs(value.imag));
    } else {
        printf("%.4f - i%.4f", value.real, fabs(value.imag));
    }
}

int main() {

    packet.samples = 12968;

    load_data(dataBuffer);

    process_data();

    print_complex(A0);
    printf(" == 0.2626 + i0.0000\n");
    print_complex(A1);
    printf(" == -0.0051 - i0.1139\n");
    print_complex(A2);
    printf(" == -0.2355 + i0.0542\n");

    printf("S0: %.5f\nS1:%.5f\nS2:%.5f\nS3:%.5f", packet.S0, packet.S1, packet.S2, packet.S3);

    // uint16_t freqCutoff = 200;
    // for (uint16_t w = 0; w < freqCutoff; w++) {
    //     struct complex res = goertzel_mag(data, samples, w, cycles);
    //     // print_complex(res);
    //     printf("%.10f\n", sqrtf(res.real * res.real + res.imag * res.imag));
    //     // printf("%u rad/s: %.5f\n", w, sqrtf(res.real * res.real + res.imag * res.imag));
    // }
    
    return 0;
}