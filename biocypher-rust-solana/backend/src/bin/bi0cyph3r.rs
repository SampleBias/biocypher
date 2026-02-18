//! Bi0cyph3r CLI — Encode and decode messages as DNA from the command line
//!
//! Usage:
//!   bi0cyph3r encode "Hello" [--mode basic|nanopore|secure] [--password PASS]
//!   bi0cyph3r decode "ATCG..." [--mode basic|nanopore|secure] [--password PASS]
//!   bi0cyph3r safety "ATCG..."

use std::process::ExitCode;

use biocypher_backend::dna::{
    basic::DNACrypto,
    nanopore::NanoporeDNACrypto,
    secure::SecureDNACrypto,
    traits::{DNACoder, SequenceStats},
    EncodingMode,
};
use biocypher_backend::safety::DNASafetyScreener;

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        print_usage(&args[0]);
        return ExitCode::FAILURE;
    }

    let subcmd = args[1].to_lowercase();
    match subcmd.as_str() {
        "encode" => run_encode(&args[2..]),
        "decode" => run_decode(&args[2..]),
        "safety" | "screen" => run_safety(&args[2..]),
        "help" | "-h" | "--help" => {
            print_usage(&args[0]);
            ExitCode::SUCCESS
        }
        _ => {
            eprintln!("Unknown command: {}", subcmd);
            print_usage(&args[0]);
            ExitCode::FAILURE
        }
    }
}

fn parse_mode(args: &[String]) -> (EncodingMode, Option<String>) {
    let mut mode = EncodingMode::Basic;
    let mut password = None;

    let mut i = 0;
    while i < args.len() {
        if args[i] == "--mode" && i + 1 < args.len() {
            mode = match args[i + 1].to_lowercase().as_str() {
                "nanopore" => EncodingMode::Nanopore,
                "secure" => EncodingMode::Secure,
                _ => EncodingMode::Basic,
            };
            i += 2;
        } else if (args[i] == "--password" || args[i] == "-p") && i + 1 < args.len() {
            password = Some(args[i + 1].clone());
            i += 2;
        } else {
            i += 1;
        }
    }
    (mode, password)
}

fn run_encode(args: &[String]) -> ExitCode {
    if args.is_empty() {
        eprintln!("Error: encode requires a message");
        eprintln!("  {} encode \"Your message\"", std::env::args().next().unwrap_or_default());
        return ExitCode::FAILURE;
    }

    let message = &args[0];
    let (mode, password) = parse_mode(args);

    if matches!(mode, EncodingMode::Secure) && password.is_none() {
        eprintln!("Error: secure mode requires --password");
        return ExitCode::FAILURE;
    }

    let result = match mode {
        EncodingMode::Basic => DNACrypto::encode_message(message),
        EncodingMode::Nanopore => NanoporeDNACrypto::encode_message(message),
        EncodingMode::Secure => {
            let pwd = password.as_ref().unwrap();
            SecureDNACrypto::encode_with_password(message, pwd)
        }
    };

    match result {
        Ok(dna) => {
            println!("{}", dna);
            let stats = match mode {
                EncodingMode::Basic => DNACrypto::get_sequence_stats(&dna),
                EncodingMode::Nanopore => NanoporeDNACrypto::get_sequence_stats(&dna),
                EncodingMode::Secure => SecureDNACrypto::get_sequence_stats(&dna),
            };
            eprintln!(
                "  [{} bases, GC: {:.1}%]",
                stats.length, stats.gc_content
            );
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            ExitCode::FAILURE
        }
    }
}

fn run_decode(args: &[String]) -> ExitCode {
    if args.is_empty() {
        eprintln!("Error: decode requires a DNA sequence");
        eprintln!("  {} decode \"ATCGATCG...\"", std::env::args().next().unwrap_or_default());
        return ExitCode::FAILURE;
    }

    let sequence = &args[0];
    let (mode, password) = parse_mode(args);

    if matches!(mode, EncodingMode::Secure) && password.is_none() {
        eprintln!("Error: secure mode requires --password");
        return ExitCode::FAILURE;
    }

    let result = match mode {
        EncodingMode::Basic => DNACrypto::decode_sequence(sequence),
        EncodingMode::Nanopore => NanoporeDNACrypto::decode_sequence(sequence),
        EncodingMode::Secure => {
            let pwd = password.as_ref().unwrap();
            SecureDNACrypto::decode_with_password(sequence, pwd)
        }
    };

    match result {
        Ok(msg) => {
            println!("{}", msg);
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            ExitCode::FAILURE
        }
    }
}

fn run_safety(args: &[String]) -> ExitCode {
    if args.is_empty() {
        eprintln!("Error: safety requires a DNA sequence");
        eprintln!("  {} safety \"ATCGATCG...\"", std::env::args().next().unwrap_or_default());
        return ExitCode::FAILURE;
    }

    let sequence = &args[0];
    let screener = DNASafetyScreener::new();
    match screener.perform_comprehensive_screening(sequence) {
        Ok(report) => {
            println!("Status: {:?}", report.safety_status);
            if !report.pathogen_analysis.matches.is_empty() {
                println!("Pathogen matches: {:?}", report.pathogen_analysis.matches);
            }
            if !report.natural_occurrence.matches.is_empty() {
                println!("Natural occurrence: {:?}", report.natural_occurrence.matches);
            }
            println!("GC content: {:.1}%", report.sequence_characteristics.gc_content);
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            ExitCode::FAILURE
        }
    }
}

fn print_usage(prog: &str) {
    let name = std::path::Path::new(prog).file_stem().and_then(|s| s.to_str()).unwrap_or("bi0cyph3r");
    eprintln!("Bi0cyph3r — DNA cryptography CLI");
    eprintln!();
    eprintln!("Usage:");
    eprintln!("  {} encode <message> [--mode basic|nanopore|secure] [--password PASS]", name);
    eprintln!("  {} decode <sequence> [--mode basic|nanopore|secure] [--password PASS]", name);
    eprintln!("  {} safety <sequence>", name);
    eprintln!();
    eprintln!("Examples:");
    eprintln!("  {} encode \"Hello World\"", name);
    eprintln!("  {} encode \"Secret\" --mode secure --password mypass", name);
    eprintln!("  {} decode \"TACATCTTTCG...\"", name);
    eprintln!("  {} safety \"ATCGATCGATCG\"", name);
}
