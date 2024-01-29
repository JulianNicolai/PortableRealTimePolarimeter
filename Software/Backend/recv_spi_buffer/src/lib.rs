// use pyo3::{buffer, prelude::*};
use pyo3::{prelude::*};
use std::io;
// use std::io::prelude::*;
use spidev::{SpiModeFlags, Spidev, SpidevOptions, SpidevTransfer};

const MAX_BUFFER_SIZE: usize = 32768;

/// Some test code to recieve SPI data.
#[pyfunction]
fn recv_packets(buffer_length: u16) -> PyResult<()> {
    let mut spi = create_spi().unwrap();
    let mut rx_buffer = [0u16; MAX_BUFFER_SIZE];
    read_spi(&mut spi, &mut rx_buffer, buffer_length).unwrap();
    PyResult::Ok(())
}

fn read_spi(spi: &mut Spidev, rx_buffer: &mut [u16], buffer_length: u16) -> io::Result<()> {
    let tx_arr = [0u8; 2];
    let mut rx_arr = [0u8; 2];
    for i in 0..buffer_length as usize {
        {
            let mut transfer = SpidevTransfer::read_write(&tx_arr, &mut rx_arr);
            spi.transfer(&mut transfer)?;
        }
        rx_buffer[i] = ((rx_arr[0] as u16) << 8) + (rx_arr[1] as u16);
    }
    Ok(())
}

fn create_spi() -> io::Result<Spidev> {
    let mut spi = Spidev::open("/dev/spidev0.0")?;  // spidev0.0 is CE0, spidev0.1 is CE1, etc.
    let options = SpidevOptions::new()
        .bits_per_word(16)
        .max_speed_hz(1000000)
        .mode(SpiModeFlags::SPI_MODE_0)
        .build();
    spi.configure(&options)?;
    Ok(spi)
}

/// A Python module implemented in Rust.
#[pymodule]
fn recv_spi_buffer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(recv_packets, m)?)?;
    Ok(())
}
