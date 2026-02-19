//! Bi0cyph3r CLI — Encode and decode messages as DNA from the command line
//!
//! Usage:
//!   bi0cyph3r encode "Hello" [--mode basic|nanopore|secure] [--password PASS]
//!   bi0cyph3r decode "ATCG..." [--mode basic|nanopore|secure] [--password PASS]
//!   bi0cyph3r safety "ATCG..."
//!   bi0cyph3r plasmid "Hello" [--mode basic|nanopore|secure] [--password PASS] [--name NAME] [--output fasta|txt|json]

use std::process::ExitCode;

use biocypher_backend::dna::{
    basic::DNACrypto,
    nanopore::NanoporeDNACrypto,
    secure::SecureDNACrypto,
    split_key::SplitKeyDNACrypto,
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
        "plasmid" => run_plasmid(&args[2..]),
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

fn parse_mode(args: &[String]) -> (EncodingMode, Option<String>, Option<String>, Option<String>) {
    let mut mode = EncodingMode::Basic;
    let mut password = None;
    let mut k1 = None;
    let mut k2 = None;

    let mut i = 0;
    while i < args.len() {
        if args[i] == "--mode" && i + 1 < args.len() {
            mode = match args[i + 1].to_lowercase().as_str() {
                "nanopore" => EncodingMode::Nanopore,
                "secure" => EncodingMode::Secure,
                "splitkey" => EncodingMode::SplitKey,
                _ => EncodingMode::Basic,
            };
            i += 2;
        } else if (args[i] == "--password" || args[i] == "-p") && i + 1 < args.len() {
            password = Some(args[i + 1].clone());
            i += 2;
        } else if args[i] == "--k1" && i + 1 < args.len() {
            k1 = Some(args[i + 1].clone());
            i += 2;
        } else if args[i] == "--k2" && i + 1 < args.len() {
            k2 = Some(args[i + 1].clone());
            i += 2;
        } else {
            i += 1;
        }
    }
    (mode, password, k1, k2)
}

fn run_encode(args: &[String]) -> ExitCode {
    if args.is_empty() {
        eprintln!("Error: encode requires a message");
        eprintln!("  {} encode \"Your message\"", std::env::args().next().unwrap_or_default());
        return ExitCode::FAILURE;
    }

    let message = &args[0];
    let (mode, password, _k1, _k2) = parse_mode(args);

    if matches!(mode, EncodingMode::Secure) && password.is_none() {
        eprintln!("Error: secure mode requires --password");
        return ExitCode::FAILURE;
    }

    let result = match mode {
        EncodingMode::Basic => DNACrypto::encode_message(message).map(|d| (d, None, None)),
        EncodingMode::Nanopore => NanoporeDNACrypto::encode_message(message).map(|d| (d, None, None)),
        EncodingMode::Secure => {
            let pwd = password.as_ref().unwrap();
            SecureDNACrypto::encode_with_password(message, pwd).map(|d| (d, None, None))
        }
        EncodingMode::SplitKey => {
            SplitKeyDNACrypto::encode_with_split_keys(message).map(|(d, k1, k2)| (d, Some(k1), Some(k2)))
        }
    };

    match result {
        Ok((dna, k1_opt, k2_opt)) => {
            println!("{}", dna);
            let stats = match mode {
                EncodingMode::Basic => DNACrypto::get_sequence_stats(&dna),
                EncodingMode::Nanopore => NanoporeDNACrypto::get_sequence_stats(&dna),
                EncodingMode::Secure => SecureDNACrypto::get_sequence_stats(&dna),
                EncodingMode::SplitKey => SplitKeyDNACrypto::get_sequence_stats(&dna),
            };
            eprintln!(
                "  [{} bases, GC: {:.1}%]",
                stats.length, stats.gc_content
            );
            if let (Some(k1), Some(k2)) = (k1_opt, k2_opt) {
                eprintln!("  K1 (save securely): {}", k1);
                eprintln!("  K2 (escrow): {}", k2);
            }
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
    let (mode, password, k1, k2) = parse_mode(args);

    if matches!(mode, EncodingMode::Secure) && password.is_none() {
        eprintln!("Error: secure mode requires --password");
        return ExitCode::FAILURE;
    }

    if matches!(mode, EncodingMode::SplitKey) && (k1.is_none() || k2.is_none()) {
        eprintln!("Error: splitkey mode requires --k1 and --k2");
        return ExitCode::FAILURE;
    }

    let result = match mode {
        EncodingMode::Basic => DNACrypto::decode_sequence(sequence),
        EncodingMode::Nanopore => NanoporeDNACrypto::decode_sequence(sequence),
        EncodingMode::Secure => {
            let pwd = password.as_ref().unwrap();
            SecureDNACrypto::decode_with_password(sequence, pwd)
        }
        EncodingMode::SplitKey => {
            let k1 = k1.as_ref().unwrap();
            let k2 = k2.as_ref().unwrap();
            SplitKeyDNACrypto::decode_with_split_keys(sequence, k1, k2)
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

#[derive(Clone, Copy, PartialEq, Eq)]
enum PlasmidOutput {
    Fasta,
    Txt,
    Json,
}

fn parse_plasmid_args(args: &[String]) -> Option<(String, EncodingMode, Option<String>, String, PlasmidOutput)> {
    let mut message = None;
    let mut mode = EncodingMode::Basic;
    let mut password = None;
    let mut name = "biocypher_plasmid".to_string();
    let mut output = PlasmidOutput::Fasta;

    let mut i = 0;
    while i < args.len() {
        if args[i] == "--mode" && i + 1 < args.len() {
            mode = match args[i + 1].to_lowercase().as_str() {
                "nanopore" => EncodingMode::Nanopore,
                "secure" => EncodingMode::Secure,
                "splitkey" => EncodingMode::SplitKey,
                _ => EncodingMode::Basic,
            };
            i += 2;
        } else if (args[i] == "--password" || args[i] == "-p") && i + 1 < args.len() {
            password = Some(args[i + 1].clone());
            i += 2;
        } else if args[i] == "--name" && i + 1 < args.len() {
            name = args[i + 1].clone();
            i += 2;
        } else if args[i] == "--output" && i + 1 < args.len() {
            output = match args[i + 1].to_lowercase().as_str() {
                "txt" | "text" => PlasmidOutput::Txt,
                "json" => PlasmidOutput::Json,
                _ => PlasmidOutput::Fasta,
            };
            i += 2;
        } else if !args[i].starts_with('-') {
            message = Some(args[i].clone());
            i += 1;
        } else {
            i += 1;
        }
    }
    message.map(|m| (m, mode, password, name, output))
}

fn wrap_fasta(seq: &str, line_len: usize) -> String {
    let mut out = String::with_capacity(seq.len() + seq.len() / line_len + 2);
    for chunk in seq.as_bytes().chunks(line_len) {
        out.push_str(std::str::from_utf8(chunk).unwrap_or(""));
        out.push('\n');
    }
    out.trim_end().to_string()
}

fn run_plasmid(args: &[String]) -> ExitCode {
    let Some((message, mode, password, name, output)) = parse_plasmid_args(args) else {
        eprintln!("Error: plasmid requires a message");
        eprintln!("  {} plasmid \"Your message\" [--name NAME] [--output fasta|txt|json]", std::env::args().next().unwrap_or_default());
        return ExitCode::FAILURE;
    };

    if matches!(mode, EncodingMode::Secure) && password.is_none() {
        eprintln!("Error: secure mode requires --password");
        return ExitCode::FAILURE;
    }

    let result = match mode {
        EncodingMode::Basic => DNACrypto::encode_message(&message).map(|s| (s, None, None)),
        EncodingMode::Nanopore => NanoporeDNACrypto::encode_message(&message).map(|s| (s, None, None)),
        EncodingMode::Secure => {
            let pwd = password.as_ref().unwrap();
            SecureDNACrypto::encode_with_password(&message, pwd).map(|s| (s, None, None))
        }
        EncodingMode::SplitKey => {
            SplitKeyDNACrypto::encode_with_split_keys(&message).map(|(s, k1, k2)| (s, Some(k1), Some(k2)))
        }
    };

    match result {
        Ok((sequence, k1_opt, k2_opt)) => {
            let stats = match mode {
                EncodingMode::Basic => DNACrypto::get_sequence_stats(&sequence),
                EncodingMode::Nanopore => NanoporeDNACrypto::get_sequence_stats(&sequence),
                EncodingMode::Secure => SecureDNACrypto::get_sequence_stats(&sequence),
                EncodingMode::SplitKey => SplitKeyDNACrypto::get_sequence_stats(&sequence),
            };
            match output {
                PlasmidOutput::Fasta => {
                    println!(">{}\n{}", name, wrap_fasta(&sequence, 80));
                }
                PlasmidOutput::Txt => {
                    println!("{}", sequence);
                }
                PlasmidOutput::Json => {
                    let mut instructions = serde_json::json!({
                        "name": name,
                        "sequence": sequence,
                        "mode": format!("{}", mode),
                        "message_length": message.len(),
                        "gc_content": stats.gc_content,
                    });
                    if let (Some(ref k1), Some(ref k2)) = (&k1_opt, &k2_opt) {
                        instructions["k1_base64"] = serde_json::json!(k1);
                        instructions["k2_base64"] = serde_json::json!(k2);
                    }
                    println!("{}", serde_json::to_string_pretty(&instructions).unwrap_or_default());
                }
            }
            if let (Some(ref k1), Some(ref k2)) = (&k1_opt, &k2_opt) {
                eprintln!("  K1 (save securely): {}", k1);
                eprintln!("  K2 (escrow): {}", k2);
            }
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
    eprintln!("  {} encode <message> [--mode basic|nanopore|secure|splitkey] [--password PASS]", name);
    eprintln!("  {} decode <sequence> [--mode basic|nanopore|secure|splitkey] [--password PASS] [--k1 K1] [--k2 K2]", name);
    eprintln!("  {} safety <sequence>", name);
    eprintln!("  {} plasmid <message> [--mode basic|nanopore|secure|splitkey] [--password PASS] [--name NAME] [--output fasta|txt|json]", name);
    eprintln!();
    eprintln!("Examples:");
    eprintln!("  {} encode \"Hello World\"", name);
    eprintln!("  {} encode \"Secret\" --mode secure --password mypass", name);
    eprintln!("  {} encode \"Secret\" --mode splitkey", name);
    eprintln!("  {} decode \"TACATCTTTCG...\"", name);
    eprintln!("  {} decode \"ATCG...\" --mode splitkey --k1 <base64> --k2 <base64>", name);
    eprintln!("  {} safety \"ATCGATCGATCG\"", name);
    eprintln!("  {} plasmid \"Hi\" --output fasta", name);
}
