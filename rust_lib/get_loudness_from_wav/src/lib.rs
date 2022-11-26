use std::fs::File;
use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn wav2loudness(file_path: &str) -> Vec<f32> {
    let file_in = File::open(file_path).unwrap();
    let (_head, samples) = wav_io::read_from_file(file_in).unwrap();
    samples.iter().map(|x| x.abs()).collect()
}

/// A Python module implemented in Rust.
#[pymodule]
fn get_loudness_from_wav(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(wav2loudness, m)?)?;
    Ok(())
}

