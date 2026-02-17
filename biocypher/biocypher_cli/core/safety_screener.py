"""
DNA Safety Screener Module
Analyzes DNA sequences for potential pathogen risks and natural occurrence
"""

import re
import hashlib
from typing import Dict, List, Tuple, Any

class SafetyScreenerError(Exception):
    """Custom exception for safety screening errors"""
    pass

class DNASafetyScreener:
    """DNA Safety Screening System"""
    
    # Known pathogen signatures (simplified patterns)
    PATHOGEN_SIGNATURES = {
        'viral_polymerase': [
            'ATGGATCCGTATGACTCC',  # Simplified viral polymerase motif
            'CCGTATGACTCCATGG',    # Reverse complement
        ],
        'toxin_genes': [
            'ATGAAGCTGTATGACCC',   # Simplified toxin gene start
            'GGGTCATACAGCTTCAT',   # Reverse complement
        ],
        'antibiotic_resistance': [
            'ATGAGCCATATTCAACG',   # Beta-lactamase-like
            'CGTTGAATATGGCTCAT',   # Reverse complement
            'ATGTCGCAGTTCGATCC',   # Aminoglycoside resistance-like
            'GGATCGAACTGCGACAT',   # Reverse complement
        ],
        'virulence_factors': [
            'ATGCTGAAACGTTATGC',   # Simplified virulence factor
            'GCATAACGTTTCAGCAT',   # Reverse complement
        ]
    }
    
    # Common housekeeping genes (simplified patterns)
    HOUSEKEEPING_GENES = {
        'ribosomal_rna': [
            'TACCTGGTTGATCCTGC',   # 16S rRNA-like
            'GCAGGATCAACCAGGTA',   # Reverse complement
        ],
        'actin': [
            'ATGGATGATGATATCGC',   # Actin-like
            'GCGATATCATCATCCAT',   # Reverse complement
        ],
        'gapdh': [
            'ATGGTGAAGGTCGGTGT',   # GAPDH-like
            'ACACCGACCTTCACCAT',   # Reverse complement
        ],
        'tubulin': [
            'ATGCGTGAGATCGTGCA',   # Tubulin-like
            'TGCACGATCTCACGCAT',   # Reverse complement
        ]
    }
    
    # E. coli genome signatures (simplified)
    ECOLI_SIGNATURES = [
        'GATCCTGGAAAGTGCAG',
        'CTGCACTTTCCAGGATC',
        'ATGAAACGCATTAGCAC',
        'GTGCTAATGCGTTTCAT'
    ]
    
    # Human genome signatures (simplified)
    HUMAN_SIGNATURES = [
        'ATGCCCTGTGATTTCGG',
        'CCGAAATCACAGGGCAT',
        'GAGCTGAAGGGCGTGAA',
        'TTCACGCCCTTCAGCTC'
    ]
    
    @staticmethod
    def reverse_complement(sequence: str) -> str:
        """Generate reverse complement of DNA sequence"""
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        return ''.join(complement.get(base, base) for base in reversed(sequence))
    
    @staticmethod
    def find_orfs(sequence: str, min_length: int = 30) -> List[Tuple[int, int, int]]:
        """Find open reading frames in sequence"""
        start_codons = ['ATG']
        stop_codons = ['TAA', 'TAG', 'TGA']
        orfs = []
        
        for frame in range(3):
            for i in range(frame, len(sequence) - 2, 3):
                codon = sequence[i:i+3]
                if codon in start_codons:
                    # Look for stop codon
                    for j in range(i + 3, len(sequence) - 2, 3):
                        stop_codon = sequence[j:j+3]
                        if stop_codon in stop_codons:
                            if j - i >= min_length:
                                orfs.append((i, j + 3, frame))
                            break
        
        return orfs
    
    @classmethod
    def check_pathogen_signatures(cls, sequence: str) -> Dict[str, Any]:
        """Check for known pathogen signatures"""
        results = {
            'pathogen_risk': False,
            'matches': [],
            'risk_level': 'low'
        }
        
        sequence_upper = sequence.upper()
        
        for category, signatures in cls.PATHOGEN_SIGNATURES.items():
            for signature in signatures:
                if signature in sequence_upper:
                    results['pathogen_risk'] = True
                    results['matches'].append({
                        'category': category,
                        'signature': signature,
                        'position': sequence_upper.find(signature)
                    })
        
        # Determine risk level
        if len(results['matches']) > 0:
            if any(match['category'] in ['toxin_genes', 'virulence_factors'] for match in results['matches']):
                results['risk_level'] = 'high'
            elif any(match['category'] == 'antibiotic_resistance' for match in results['matches']):
                results['risk_level'] = 'medium'
            else:
                results['risk_level'] = 'low'
        
        return results
    
    @classmethod
    def check_natural_occurrence(cls, sequence: str) -> Dict[str, Any]:
        """Check if sequence occurs naturally"""
        results = {
            'natural_occurrence': False,
            'matches': [],
            'organisms': []
        }
        
        sequence_upper = sequence.upper()
        
        # Check housekeeping genes
        for gene_type, signatures in cls.HOUSEKEEPING_GENES.items():
            for signature in signatures:
                if signature in sequence_upper:
                    results['natural_occurrence'] = True
                    results['matches'].append({
                        'type': 'housekeeping_gene',
                        'gene': gene_type,
                        'signature': signature,
                        'position': sequence_upper.find(signature)
                    })
                    results['organisms'].append('Multiple species (housekeeping)')
        
        # Check E. coli signatures
        for signature in cls.ECOLI_SIGNATURES:
            if signature in sequence_upper:
                results['natural_occurrence'] = True
                results['matches'].append({
                    'type': 'genome_signature',
                    'organism': 'E. coli',
                    'signature': signature,
                    'position': sequence_upper.find(signature)
                })
                if 'E. coli' not in results['organisms']:
                    results['organisms'].append('E. coli')
        
        # Check human signatures
        for signature in cls.HUMAN_SIGNATURES:
            if signature in sequence_upper:
                results['natural_occurrence'] = True
                results['matches'].append({
                    'type': 'genome_signature',
                    'organism': 'Human',
                    'signature': signature,
                    'position': sequence_upper.find(signature)
                })
                if 'Human' not in results['organisms']:
                    results['organisms'].append('Human')
        
        return results
    
    @classmethod
    def analyze_sequence_characteristics(cls, sequence: str) -> Dict[str, Any]:
        """Analyze sequence characteristics for safety"""
        results = {
            'length': len(sequence),
            'gc_content': 0,
            'homopolymer_runs': [],
            'orfs': [],
            'repetitive_elements': [],
            'warnings': []
        }
        
        if not sequence:
            return results
        
        # Calculate GC content
        gc_count = sequence.count('G') + sequence.count('C')
        results['gc_content'] = round((gc_count / len(sequence)) * 100, 2)
        
        # Check for extreme GC content
        if results['gc_content'] < 20 or results['gc_content'] > 80:
            results['warnings'].append(f"Extreme GC content: {results['gc_content']}%")
        
        # Find homopolymer runs (4+ consecutive same bases)
        for base in 'ATCG':
            pattern = base + '{4,}'
            for match in re.finditer(pattern, sequence):
                results['homopolymer_runs'].append({
                    'base': base,
                    'length': len(match.group()),
                    'position': match.start()
                })
                if len(match.group()) >= 6:
                    results['warnings'].append(f"Long homopolymer run: {len(match.group())} {base}s")
        
        # Find ORFs
        results['orfs'] = cls.find_orfs(sequence)
        if len(results['orfs']) > 0:
            results['warnings'].append(f"Found {len(results['orfs'])} potential protein-coding sequences")
        
        # Check for repetitive elements (simple repeat detection)
        for i in range(3, min(20, len(sequence) // 3)):
            pattern = sequence[:i]
            if sequence.count(pattern) >= 3:
                results['repetitive_elements'].append({
                    'pattern': pattern,
                    'count': sequence.count(pattern),
                    'length': len(pattern)
                })
        
        if results['repetitive_elements']:
            results['warnings'].append("Repetitive elements detected")
        
        return results
    
    @classmethod
    def perform_comprehensive_screening(cls, sequence: str) -> Dict[str, Any]:
        """Perform comprehensive safety screening"""
        if not sequence or not sequence.strip():
            raise SafetyScreenerError("Empty sequence provided")
        
        # Clean sequence
        clean_sequence = re.sub(r'[^ATCG]', '', sequence.upper())
        if not clean_sequence:
            raise SafetyScreenerError("No valid DNA bases found in sequence")
        
        # Perform all checks
        pathogen_check = cls.check_pathogen_signatures(clean_sequence)
        natural_check = cls.check_natural_occurrence(clean_sequence)
        characteristics = cls.analyze_sequence_characteristics(clean_sequence)
        
        # Determine overall safety status
        safety_status = "SAFE"
        safety_color = "green"
        safety_icon = "✅"
        
        if pathogen_check['pathogen_risk']:
            if pathogen_check['risk_level'] == 'high':
                safety_status = "UNSAFE"
                safety_color = "red"
                safety_icon = "❌"
            else:
                safety_status = "CAUTION"
                safety_color = "orange"
                safety_icon = "⚠️"
        elif natural_check['natural_occurrence']:
            safety_status = "CAUTION"
            safety_color = "orange"
            safety_icon = "⚠️"
        elif len(characteristics['warnings']) > 2:
            safety_status = "CAUTION"
            safety_color = "orange"
            safety_icon = "⚠️"
        
        # Compile comprehensive report
        report = {
            'sequence_length': len(clean_sequence),
            'safety_status': safety_status,
            'safety_color': safety_color,
            'safety_icon': safety_icon,
            'pathogen_analysis': pathogen_check,
            'natural_occurrence': natural_check,
            'sequence_characteristics': characteristics,
            'recommendations': cls._generate_recommendations(
                pathogen_check, natural_check, characteristics, safety_status
            ),
            'timestamp': cls._get_timestamp()
        }
        
        return report
    
    @staticmethod
    def _generate_recommendations(pathogen_check: Dict, natural_check: Dict, 
                                characteristics: Dict, safety_status: str) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        if safety_status == "SAFE":
            recommendations.append("✅ Sequence appears safe for synthesis")
            recommendations.append("✅ No pathogen signatures detected")
            recommendations.append("✅ No natural genome matches found")
        
        if pathogen_check['pathogen_risk']:
            recommendations.append("❌ DO NOT SYNTHESIZE - Pathogen signatures detected")
            recommendations.append("🔬 Consult biosafety experts before proceeding")
        
        if natural_check['natural_occurrence']:
            recommendations.append("⚠️ Sequence matches natural genomes")
            recommendations.append("🧬 Consider modifying to avoid natural sequences")
        
        if characteristics['gc_content'] < 20 or characteristics['gc_content'] > 80:
            recommendations.append("⚠️ Extreme GC content may affect synthesis")
        
        if len(characteristics['orfs']) > 0:
            recommendations.append("🧬 Contains potential protein-coding sequences")
        
        if len(characteristics['homopolymer_runs']) > 5:
            recommendations.append("⚠️ Multiple homopolymer runs detected")
        
        return recommendations
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")