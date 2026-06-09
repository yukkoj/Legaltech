"""Example usage of the Legal Document Creator framework."""
import uuid
from dotenv import load_dotenv
from orchestrator import DocumentOrchestrator
from models.document import LegalDocument


def example_nda():
    """Example: Create a Non-Disclosure Agreement (NDA)."""
    load_dotenv()
    
    # Initialize orchestrator
    orchestrator = DocumentOrchestrator(
        num_edit_passes=1  # Set to 2 or more for multiple editing passes
    )
    
    # Create document requirements
    requirements = """
    - Confidentiality obligations for both parties
    - 2-year term for confidentiality
    - Exceptions: publicly available information, independently developed info
    - Permitted disclosures: to employees and advisors under similar obligations
    - Return or destruction of confidential information upon termination
    - Governing law: State of California
    - Mutual NDA (both parties are bound)
    - Include a one-year tail period for inadvertent disclosures
    - Remedies: injunctive relief and damages
    """
    
    # Create document
    document = LegalDocument(
        id=str(uuid.uuid4())[:8],
        document_type="Non-Disclosure Agreement",
        requirements=requirements
    )
    
    # Process through multi-agent pipeline
    result = orchestrator.create_document(document)
    
    # Save to file
    output_path = orchestrator.save_document(result)
    
    print(f"\nDocument saved to: {output_path}")
    print(f"Total versions created: {result.current_version}")
    
    return result


def example_employment_contract():
    """Example: Create an Employment Contract."""
    load_dotenv()
    
    orchestrator = DocumentOrchestrator(
        num_edit_passes=2  # Two editing passes for more refinement
    )
    
    requirements = """
    - Position: Senior Software Engineer
    - Employment type: Full-time
    - Start date: January 1, 2024
    - Salary: $150,000 annually, paid bi-weekly
    - Benefits: Health insurance, 401k with company match, PTO 20 days/year
    - Equity: Stock options vesting over 4 years
    - Non-compete clause: 6 months within 50 miles
    - At-will employment with 2 weeks notice
    - Remote work allowed 2 days per week
    - Professional development budget: $2,500/year
    - Intellectual property: All work created belongs to company
    """
    
    document = LegalDocument(
        id=str(uuid.uuid4())[:8],
        document_type="Employment Contract",
        requirements=requirements
    )
    
    result = orchestrator.create_document(document)
    output_path = orchestrator.save_document(result)
    
    print(f"\nDocument saved to: {output_path}")
    print(f"Total versions created: {result.current_version}")
    
    return result


if __name__ == "__main__":
    print("=" * 80)
    print("Legal Document Creator - Multi-Agent Framework")
    print("=" * 80)
    
    # Uncomment to run examples
    # print("\n[EXAMPLE 1] Creating NDA...")
    # example_nda()
    
    # print("\n[EXAMPLE 2] Creating Employment Contract...")
    # example_employment_contract()
    
    print("\nTo use this framework:")
    print("1. Set your GEMINI_API_KEY in .env file")
    print("2. Create a LegalDocument with your requirements")
    print("3. Initialize DocumentOrchestrator")
    print("4. Call orchestrator.create_document()")
    print("5. Optionally save with orchestrator.save_document()")
