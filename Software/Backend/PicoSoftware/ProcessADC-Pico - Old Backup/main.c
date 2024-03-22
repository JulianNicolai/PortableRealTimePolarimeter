#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/spi.h"
#include "hardware/uart.h"
#include <string.h>
#include <math.h>

#define PIN_HALL        22  // Hall effect sensor pin
#define BUFFER_LENGTH   100000  // Size of ADC data buffer

// SPI pins (to ADC)
#define SPI_PORT        spi0  // SPI port to use (spi0/spi1)
#define SPI_CLOCK_SPEED 20000000  // Clock speed of SPI bus
#define PIN_RX          4  // SPI RX pin (MISO)
#define PIN_ADC_CS      5  // SPI CS pin -> ADC conversion pin
#define PIN_SCK         6  // SPI clock pin (SCLK)
#define PIN_TX          7  // SPI TX pin (MOSI)

// UART communication pins (to RPi 4)
#define UART_ID         uart0  // UART port to use (uart0/uart1)
#define BAUD_RATE       115200  // UART baud rate (symbols/s)
#define DATA_BITS       8  // Number of data bits in a packet
#define STOP_BITS       1  // Number of stop bits in a packet
#define PARITY          UART_PARITY_NONE  // Don't use parity bit
#define UART_TX_PIN     12  // UART TX pin
#define UART_RX_PIN     13  // UART RX pin

// Define a custom data packet to send back to RPi 4 
// -> contains Stokes parameters and statistics
struct DataPacket {
    char start[4];
    uint32_t samples;
    uint32_t dt;
    float S0;
    float S1;
    float S2;
    float S3;
};

// Used to represent complex valued numbers
struct complex {
    float real;
    float imag;
};

static struct complex A0, A1, A2;
static struct DataPacket packet = {{'$', '$', '$', '$'}, 46263, 57236, 512.231, 876.254, 856.297, 897.847};

static const int PACKET_SIZE = sizeof(packet);
static const uint16_t WRITE_BIT = 0;
static const float normalisationFactor = 1 / 65535.0;
static const float M_PI2 = 2.0 * 3.14159265358979323846;

// global parameters used to compute Goertzel's algorithm
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

static uint8_t num_cycles = 5;
static uint8_t packet_array[sizeof(packet)];
static uint8_t clkVal = 0;
static bool activeGatherEvent = false;
static uint16_t dataBuffer[BUFFER_LENGTH] = {0};

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
    omega1 = 2.0 * num_cycles * M_PI2 * numSamplesI;
    omega2 = 2.0 * omega1;
    sine1 = sin(omega1);
    sine2 = sin(omega2);
    cosine1 = cos(omega1);
    cosine2 = cos(omega2);
    coeff1 = 2.0 * cosine1;
    coeff2 = 2.0 * cosine2;
}

void apply_window() {
    // Applies a Welch (parabolic) window function
    float A, B;
    int n = 0;
    for (n = 0; n < packet.samples; n++) {
        A = n * 2.0 * numSamplesI - 1;
        B = 1.0 - A * A;
        dataBuffer[n] = dataBuffer[n] * B * 1.5;  // 1.5 amplitude correction factor (1/mean of window function)
    }
}

void goertzel() {
    // Computes the complex frequency amplitude at 0, 2w, and 4w
    // Uses Goertzel's algorithm

    q0_1 = 0.0;
    q1_1 = 0.0;
    q2_1 = 0.0;
    
    q0_2 = 0.0;
    q1_2 = 0.0;
    q2_2 = 0.0;

    float total = 0.0;
    float value;
    int i;
    for (i = 0; i < packet.samples; i++) {
        value = (float) dataBuffer[i];

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

static inline void cs_adc_select() {
    gpio_put(PIN_ADC_CS, 0);  // Active low
}

static inline void cs_adc_deselect() {
    gpio_put(PIN_ADC_CS, 1);
}

void send_packet() {
    memcpy(packet_array, &packet, PACKET_SIZE);
    uart_write_blocking(UART_ID, packet_array, PACKET_SIZE);
}

uint16_t read_adc() {
    uint16_t adcVal = 0; 

    cs_adc_select();
    spi_read16_blocking(SPI_PORT, WRITE_BIT, &adcVal, 1);
    cs_adc_deselect();

    return adcVal;
}

void gpio_callback(uint gpio, uint32_t events) {
    switch (gpio) {

    case PIN_HALL:
        if (clkVal < num_cycles) {
            clkVal++;
            if (clkVal == 1) {
                activeGatherEvent = true;
            }
        } else {
            clkVal = 0;
            activeGatherEvent = false;
        }

        // uint32_t msSinceBoot = to_ms_since_boot(get_absolute_time());
        // printf("Clk: %d, ADC: %d, ms: %d\n", clkVal, adcVal, msSinceBoot);
        break;
    
    default:
        break;
    }
}

// RX interrupt handler
void uart_rx_callback() {
    if (uart_is_readable(UART_ID)) {
        uint8_t ch = uart_getc(UART_ID);
        if (uart_is_readable(UART_ID)) {
            switch (ch)
            {
            case 'c':
                num_cycles = uart_getc(UART_ID);
                break;
            
            default:
                break;
            }
        }
    }
}

void process_buffer(uint32_t samples, uint64_t dt) {
    packet.samples = samples;
    packet.dt = (uint32_t) dt;
    compute_params();
    // apply_window(); // Applies Welch window (polynomial)
    goertzel();
    compute_stokes();
    
    // statistics(samples, dt);
}

void statistics(uint32_t samples, uint64_t dt) {
    // float sampsPerSec = (float) (samples * 1000) / dt;
    uint16_t min = dataBuffer[0];
    uint16_t max = dataBuffer[0];
    uint32_t total = 0;
    for (int i = 0; i < samples; i++) {
        uint16_t val = dataBuffer[i];
        total = total + val;
        if (val < min) {
            min = val;
        } else if (val > max) {
            max = val;
        }
    }
    float avg = (float) total / samples;
    
    // printf("S: %u, t: %u, val: %u, total: %u, avg: %.2f\n", sampleNum, t1 - t0, val, total, avg);
    // printf("ksps: %.2f, avg: %.2f, -: %u, +: %u, d: %u\n", sampsPerSec, avg, min, max, max-min);
    printf("ksps: %u, avg: %.2f, -: %u, +: %u, d: %u\n", samples, avg, min, max, max-min);
}

int main() {
    stdio_init_all();

    // Sets hall effect sensor IRQ
    gpio_set_irq_enabled_with_callback(PIN_HALL, GPIO_IRQ_EDGE_RISE, true, &gpio_callback);

    // SPI SETUP START ========================================================
    // Initializes SPI0 at 20MHz
    spi_init(SPI_PORT, SPI_CLOCK_SPEED);
    gpio_set_function(PIN_RX, GPIO_FUNC_SPI);
    gpio_set_function(PIN_SCK, GPIO_FUNC_SPI);
    gpio_set_function(PIN_TX, GPIO_FUNC_SPI);  // Unused pin (ADC does not receive)

    // Sets SPI bits, polarity, phase, and bit order (MSB is first bit)
    spi_set_format(SPI_PORT, 16, SPI_CPOL_0, SPI_CPHA_1, SPI_MSB_FIRST);

    gpio_init(PIN_ADC_CS);  // Initialise CS pin
    gpio_set_dir(PIN_ADC_CS, GPIO_OUT);  // Set mode to output
    cs_adc_deselect();  // Set low (active high)
    // SPI SETUP END ==========================================================

    // UART SETUP START =======================================================
    // Initializes UART at 115200 symbols/s
    uart_init(UART_ID, BAUD_RATE);

    // Set the TX and RX pins
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    uart_set_hw_flow(UART_ID, false, false); // Set UART flow control CTS/RTS
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY); // Set data format
    uart_set_fifo_enabled(UART_ID, true);  // Turn on FIFO's

    // Set up and enable the interrupt handlers
    irq_set_exclusive_handler(UART0_IRQ, uart_rx_callback);
    irq_set_enabled(UART0_IRQ, true);

    // Enable the UART to send interrupts - RX only
    uart_set_irq_enables(UART_ID, true, false);
    // UART SETUP END =========================================================

    // MAIN LOOP ==============================================================
    while (1) {
        uint32_t sampleNum = 0;
        if (activeGatherEvent) {
            uint64_t t0 = to_us_since_boot(get_absolute_time());
            while (activeGatherEvent) {
                dataBuffer[sampleNum] = read_adc();
                if (++sampleNum >= BUFFER_LENGTH) {
                    activeGatherEvent = false;
                };
                busy_wait_us_32(4); // Stops oversampling, total ADC read time must be under 5 us (250ksps).
                // In reality, well under 200ksps (i.e. 170ksps) is needed for a very low error rate.
            }
            uint64_t t1 = to_us_since_boot(get_absolute_time());
            process_buffer(sampleNum, t1 - t0);
            send_packet();
        }
    };
}