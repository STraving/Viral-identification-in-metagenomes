from Bio import SeqIO
import os
import glob

# ---- USER CONFIG ----
input_folder = "/path/to/assemblies"  # folder containing your .fa files
output_folder = "/path/to/renamed"    # folder to save renamed fasta files
os.makedirs(output_folder, exist_ok=True)

# Mapping key: original sample string -> compact ID
# the ID code is a two digit trench identifier ("AT"), two digit station number and depth in cm signified by "D"
sample_key = {
    "Complete_Site_1_Depth_0": "AT01D00",
    "Complete_Site_1_Depth_1": "AT01D01",
    "Complete_Site_3_Depth_0": "AT03D00",
    "Complete_Site_3_Depth_1": "AT02D01",
    # Add all your samples here
}

# ---- PROCESSING ----
unmatched_samples = set()  # store headers not found in the key

for fasta_file in glob.glob(os.path.join(input_folder, "*.fa")) + glob.glob(os.path.join(input_folder, "*.fasta")):
    basename = os.path.basename(fasta_file)
    output_file = os.path.join(output_folder, basename.replace(".fa", "_renamed.fa").replace(".fasta", "_renamed.fa"))

    with open(fasta_file) as infile, open(output_file, "w") as outfile:
        for record in SeqIO.parse(infile, "fasta"):
            # Split the header: sample part + contig ID
            parts = record.id.rsplit("_", 1)
            if len(parts) != 2:
                unmatched_samples.add(record.id)
                continue  # skip this contig
            
            sample_part, contig_id = parts
            new_sample = sample_key.get(sample_part)
            if new_sample is None:
                unmatched_samples.add(sample_part)
                continue  # skip this contig
            
            # Create new header
            record.id = f"{new_sample}_c{contig_id}"
            record.description = ""
            SeqIO.write(record, outfile, "fasta")

    print(f"Processed {basename} -> {os.path.basename(output_file)}")

# ---- REPORT UNMATCHED ----
if unmatched_samples:
    print("\nWarning: the following sample headers were not matched in the key:")
    for s in sorted(unmatched_samples):
        print(s)
else:
    print("\nAll headers matched and processed successfully.")
