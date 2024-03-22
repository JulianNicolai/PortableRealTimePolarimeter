#include "pico/stdlib.h"
#include "pico/printf.h"
#include "hardware/uart.h"
#include "hardware/irq.h"
#include <string.h>


#define UART_ID uart0
#define BAUD_RATE 115200
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_NONE

// We are using pins 0 and 1, but see the GPIO function select table in the
// datasheet for information on which other pins can be used.
#define UART_TX_PIN 12
#define UART_RX_PIN 13

static int chars_rxed = 0;

struct DataPacket {
    char start[4];
    uint32_t samples;
    uint32_t dt;
    float S0;
    float S1;
    float S2;
    float S3;
};

static struct DataPacket packet = {{'$', '$', '$', '$'}, 46263, 57236, 512.231, 876.254, 856.297, 897.847};
static const int PACKET_SIZE = sizeof(packet);
static uint8_t packet_array[sizeof(packet)];

// RX interrupt handler
void on_uart_rx() {
    while (uart_is_readable(UART_ID)) {
        uint8_t ch = uart_getc(UART_ID);
        // Can we send it back?
        if (uart_is_writable(UART_ID)) {
            // Change it slightly first!
            ch++;
            uart_putc(UART_ID, ch);
        }
        chars_rxed++;
    }
}

int main() {
    // Set up our UART with a basic baud rate.
    uart_init(UART_ID, BAUD_RATE);

    // Set the TX and RX pins by using the function select on the GPIO
    // Set datasheet for more information on function select
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);

    // Set UART flow control CTS/RTS, we don't want these, so turn them off
    uart_set_hw_flow(UART_ID, false, false);

    // Set our data format
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);

    // Turn off FIFO's - we want to do this character by character
    uart_set_fifo_enabled(UART_ID, true);

    // Set up a RX interrupt
    // We need to set up the handler first
    // Select correct interrupt for the UART we are using
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;

    // And set up and enable the interrupt handlers
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);

    // Now enable the UART to send interrupts - RX only
    uart_set_irq_enables(UART_ID, true, false);

    // OK, all set up.
    // Lets send a basic string out, and then run a loop and wait for RX interrupts
    // The handler will count them, but also reflect the incoming data back with a slight change!
    // uart_puts(UART_ID, "Hello, uart interrupts\n");

    uint64_t t0 = 0;
    uint64_t t1 = 0;
    uint64_t k = -25;
    packet.samples = (uint32_t) PACKET_SIZE;

    while (1) {
        t0 = to_us_since_boot(get_absolute_time());

        memcpy(packet_array, &packet, PACKET_SIZE);
        uart_write_blocking(UART_ID, packet_array, PACKET_SIZE);

        t1 = to_us_since_boot(get_absolute_time());

        packet.dt = (uint32_t) (t1 - t0 + k);
        sleep_ms(50);
        if (k < 25) {
            k++;
        } else {
            k = -25;
        }
    }
}

