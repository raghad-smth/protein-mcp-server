from Bio import SeqIO
import pandas as pd

file_path = r"data/uniprotkb_reviewed_true_AND_organism_id_2026_03_01.fasta"

data = []


for record in SeqIO.parse(file_path, "fasta"):

    header = record.description

    # Entry ID
    entry = record.id.split("|")[1] if "|" in record.id else record.id

    # Split main annotation section
    parts = header.split(" OS=")

    # Clean protein name
    protein_name = parts[0].replace(f">{record.id}", "").replace("sp|", "").strip()

    organism = None
    taxonomy_id = None
    gene = None
    protein_evidence = None
    sequence_version = None

    if len(parts) > 1:

        meta = "OS=" + parts[1]

        if " GN=" in meta:
            gene = meta.split(" GN=")[1].split(" PE=")[0]

        if " PE=" in meta:
            protein_evidence = meta.split(" PE=")[1].split(" SV=")[0]

        if " SV=" in meta:
            sequence_version = meta.split(" SV=")[1]

    data.append({
        "entry": entry,
        "protein_name": protein_name,
        "gene": gene,
        "protein_evidence": protein_evidence,
        "sequence_version": sequence_version,
        "sequence": str(record.seq),
        "length": len(record.seq)
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save cleaned dataset
df.to_csv("protein_database_clean.csv", index=False)

print("✅ Clean protein database created!")
print(f"✅ Total proteins parsed: {len(df)}")