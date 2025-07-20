#!/usr/bin/env python3
"""Prepare CV dataset for training"""

import os
import sys
import argparse
import zipfile
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from data.cv_generator import CVGenerator


def main():
    parser = argparse.ArgumentParser(description='Generate CV dataset for training')
    parser.add_argument('--num_cvs', type=int, default=500,
                       help='Number of CVs to generate')
    parser.add_argument('--output_dir', type=str, default='cv_dataset',
                       help='Output directory for CVs')
    parser.add_argument('--create_zip', action='store_true',
                       help='Create zip file of dataset')
    parser.add_argument('--quality_distribution', type=str,
                       help='Quality distribution (e.g., "excellent:0.2,good:0.3,average:0.3,below_average:0.2")')
    
    args = parser.parse_args()
    
    print(f"🚀 Generating {args.num_cvs} CVs...")
    
    # Parse quality distribution if provided
    quality_weights = {
        'excellent': 0.2,
        'good': 0.3,
        'average': 0.3,
        'below_average': 0.2
    }
    
    if args.quality_distribution:
        pairs = args.quality_distribution.split(',')
        quality_weights = {}
        for pair in pairs:
            quality, weight = pair.split(':')
            quality_weights[quality] = float(weight)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize generator
    generator = CVGenerator()
    
    # Generate CVs
    domains = ['data_science', 'software_engineering', 'marketing', 'finance']
    experience_levels = ['entry', 'mid', 'senior', 'executive']
    
    cv_count = 0
    
    for i in range(args.num_cvs):
        # Select parameters based on distribution
        import random
        
        # Select quality based on weights
        qualities = list(quality_weights.keys())
        weights = list(quality_weights.values())
        quality = random.choices(qualities, weights=weights)[0]
        
        # Random domain and experience
        domain = random.choice(domains)
        experience_level = random.choice(experience_levels)
        
        # Generate CV
        cv_data = generator.generate_cv(domain, experience_level, quality)
        
        # Save CV text
        cv_filename = f"cv_{i+1:04d}.txt"
        cv_path = output_dir / cv_filename
        with open(cv_path, 'w', encoding='utf-8') as f:
            f.write(cv_data['cv_text'])
        
        # Save persona metadata
        import json
        persona_filename = f"persona_{i+1:04d}.json"
        persona_path = output_dir / persona_filename
        with open(persona_path, 'w', encoding='utf-8') as f:
            json.dump({
                'persona': cv_data['persona'],
                'metadata': cv_data['metadata'],
                'quality_tier': quality,
                'domain': domain,
                'experience_level': experience_level
            }, f, indent=2)
        
        cv_count += 1
        
        if cv_count % 100 == 0:
            print(f"  Generated {cv_count}/{args.num_cvs} CVs...")
    
    print(f"✅ Generated {cv_count} CVs in {output_dir}")
    
    # Create metadata file
    metadata = {
        'total_cvs': cv_count,
        'quality_distribution': quality_weights,
        'domains': domains,
        'experience_levels': experience_levels
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create zip if requested
    if args.create_zip:
        zip_filename = f"{args.output_dir}.zip"
        print(f"📦 Creating zip file: {zip_filename}")
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in output_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(output_dir.parent)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Created {zip_filename}")
    
    print("\n🎉 Dataset preparation complete!")
    print(f"Next step: python training/train_hybrid.py --cv_dataset_path {args.output_dir}")


if __name__ == "__main__":
    main()

