add_executable(uart_test
        uart_test.c
        )

# pull in common dependencies and additional uart hardware support
target_link_libraries(uart_test pico_stdlib pico_printf hardware_uart)

# create map/bin/hex file etc. 
pico_add_extra_outputs(uart_test)

# add url via pico_set_program_url
example_auto_set_url(uart_test)
