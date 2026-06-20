"""Test fixtures and configuration for Contract Intelligence System tests."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_contract_text() -> str:
    """Sample contract text for testing.
    
    Returns:
        Sample contract text with various clauses.
    """
    return """
    SERVICE AGREEMENT
    
    This Service Agreement ("Agreement") is entered into as of January 1, 2024, 
    by and between Acme Corporation, a Delaware corporation ("Company"), and 
    TechStart Inc., a California corporation ("Provider").
    
    1. CONFIDENTIALITY
    Both parties agree to maintain all confidential information in strict confidence. 
    Neither party shall disclose any proprietary or trade secret information to third 
    parties without prior written consent. All confidential information shall be 
    returned upon termination of this agreement.
    
    2. TERMINATION
    Either party may terminate this agreement with 30 days written notice. 
    Immediate termination is permitted in case of material breach. This agreement 
    shall expire on December 31, 2024 unless terminated earlier.
    
    3. INDEMNIFICATION
    Provider shall indemnify and hold harmless Company from any third party claims, 
    losses, damages, or expenses arising out of or relating to Provider's services. 
    This includes reasonable legal fees and costs of defense.
    
    4. LIMITATION OF LIABILITY
    In no event shall either party's total liability exceed $100,000. Neither party 
    shall be liable for consequential, incidental, or indirect damages. Maximum 
    liability is limited to amounts paid under this agreement.
    
    5. GOVERNING LAW
    This agreement shall be governed by the laws of the State of New York. 
    Any disputes shall be subject to the exclusive jurisdiction of courts located 
    in New York County. Binding arbitration shall be conducted in New York City.
    
    Payment terms: Net 30 days. Total contract value: $500,000.
    """


@pytest.fixture
def empty_text() -> str:
    """Empty text for edge case testing."""
    return ""


@pytest.fixture
def data_dir() -> Path:
    """Get the data directory path.
    
    Returns:
        Path to data directory.
    """
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def sample_pdf_path(data_dir: Path) -> Path:
    """Get path to sample PDF (if exists).
    
    Returns:
        Path to sample PDF file.
    """
    sample_dir = data_dir / "sample_contracts"
    sample_dir.mkdir(parents=True, exist_ok=True)
    return sample_dir / "sample_contract.pdf"


@pytest.fixture
def test_output_dir() -> Path:
    """Get test output directory.
    
    Returns:
        Path to test output directory.
    """
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
