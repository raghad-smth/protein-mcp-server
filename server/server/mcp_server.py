import pandas as pd
from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP server
mcp = FastMCP("protein-server")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "protein_database_clean.csv"))

README = """
# Bio Intro

## What is DNA?

It is the genetic information inside the cells of the body that helps make people who they are. Think of DNA as instructions for how to make the body, like the blueprints for a house.

## What is a Cell?

A cell is a tiny living unit inside the body where biological processes happen. 

## What is a Gene?

A gene is a section inside DNA that contains instructions to build one specific protein.

## What are Amino Acids?

Amino acids are the small building blocks that connect together to form proteins. Think of them like LEGO pieces that form a structure.

## What is a Protein?

A protein is a small biological machine made of amino acids arranged in a specific sequence. Proteins help perform many functions inside the body.

---

## Kitchen Analogy

Imagine the body as a big kitchen:

* DNA -> **recipe book**.
* Genes ->  **specific recipes** inside the book.
* Amino acids -> **ingredients**.
* Proteins -> **finished dishes** ( made using the ingredients).
* The cell -> **kitchen where cooking happens**.
* The "chef" is the biological system that reads DNA and builds proteins.

---

## Dataset Table Explanation

| Column           | Meaning                                             |
| ---------------- | --------------------------------------------------- |
| entry            | Unique protein ID (like a database passport number) |
| protein_name     | Human readable description of the protein           |
| gene             | The DNA instruction page that produces the protein  |
| protein_evidence | Scientific confidence level that the protein exists |
| sequence_version | Version number of protein annotation updates        |
| sequence         | The amino acid chain that forms the protein         |
| length           | Number of amino acids in the protein                |

## Dataset Source

You can explore more protein datasets and variants from UniProt:
https://www.uniprot.org/uniprotkb?dir=ascend&query=reviewed%3Atrue+AND+organism_id%3A9606+AND+keyword%3A%22Kinase%22&sort=length
"""

# -------------------------
# Resource: README / Bio Guide
# -------------------------
@mcp.resource("protein://readme")
def get_readme() -> str:
    """
    Returns the biology introduction and dataset documentation.
    Explains DNA, genes, proteins, amino acids, and the dataset schema.
    """
    return README


# -------------------------
# Prompt: Analyze Protein
# -------------------------
@mcp.prompt()
def analyze_protein(entry_id: str) -> str:
    """
    A prompt template to analyze a specific protein by entry ID.
    """
    return f"""You are a helpful bioinformatics assistant.

Using the protein database tools available to you:
1. Look up the protein with entry ID: {entry_id}
2. Summarize its name, gene, length, and evidence level in simple terms
3. Comment on whether it is short or long compared to a typical protein
4. Explain what the evidence level means for confidence in this protein's existence

Use the protein://readme resource for biological context if needed.
"""


# -------------------------
# Prompt: Compare Genes
# -------------------------
@mcp.prompt()
def compare_genes(gene1: str, gene2: str) -> str:
    """
    A prompt template to compare two genes from the database.
    """
    return f"""You are a helpful bioinformatics assistant.

Using the protein database tools available to you:
1. Search for proteins associated with gene: {gene1}
2. Search for proteins associated with gene: {gene2}
3. Compare them side by side: number of proteins, lengths, evidence levels
4. Summarize the key differences and similarities in simple terms
"""


# -------------------------
# Tool 1: Get Protein
# -------------------------
@mcp.tool()
async def get_protein(entry_id: str):
    """
    Retrieve protein metadata by its unique entry ID.

    Parameters:
        entry_id (str): The unique protein entry identifier.

    Returns:
        dict: Protein metadata including name, gene, sequence, and length.
    """
    result = df[df["entry"] == entry_id]
    if result.empty:
        return {"error": "Protein not found"}
    return result.iloc[0].to_dict()


# -------------------------
# Tool 2: Search Gene
# -------------------------
@mcp.tool()
async def search_gene(gene: str):
    """
    Search proteins by gene name (case-insensitive).

    Parameters:
        gene (str): Gene name or partial gene match.

    Returns:
        list[dict]: List of matching proteins.
    """
    result = df[df["gene"].str.contains(gene, case=False, na=False)]
    return result.to_dict(orient="records")


# -------------------------
# Tool 3: Search by Length
# -------------------------
@mcp.tool()
async def search_by_length(min_length: int, max_length: int):
    """
    Find proteins within a specific length range.

    Parameters:
        min_length (int): Minimum protein length.
        max_length (int): Maximum protein length.

    Returns:
        list[dict]: List of matching proteins.
    """
    result = df[(df["length"] >= min_length) & (df["length"] <= max_length)]
    if result.empty:
        return {"error": f"No proteins found between length {min_length} and {max_length}"}
    return result.to_dict(orient="records")


# -------------------------
# Tool 4: Search by Evidence Level
# -------------------------
@mcp.tool()
async def search_by_evidence_level(level: int):
    """
    Filter proteins by evidence level (1-5).

    Parameters:
        level (int): Protein existence evidence level.
                     1 = Confirmed at protein level
                     2 = Confirmed at transcript level
                     3 = Inferred by homology
                     4 = Predicted
                     5 = Uncertain

    Returns:
        list[dict]: List of proteins at that evidence level.
    """
    result = df[df["protein_evidence"] == level]
    if result.empty:
        return {"error": f"No proteins found with evidence level {level}"}
    return result[["entry", "protein_name", "gene", "length"]].to_dict(orient="records")


# -------------------------
# Tool 5: Database Summary
# -------------------------
@mcp.tool()
async def database_summary():
    """
    Get a high-level summary of the protein database.

    Returns:
        dict: Total proteins, unique genes, evidence level breakdown, length stats.
    """
    summary = {
        "total_proteins": len(df),
        "unique_genes": df["gene"].nunique(),
        "evidence_level_breakdown": df["protein_evidence"].value_counts().to_dict(),
        "length_stats": {
            "min": int(df["length"].min()),
            "max": int(df["length"].max()),
            "average": round(float(df["length"].mean()), 2),
            "median": float(df["length"].median())
        }
    }
    return summary


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="stdio")