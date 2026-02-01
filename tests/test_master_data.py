import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generators.master_data import generate_customer_data, NUM_CUSTOMERS


def test_customer_generation_counts():
    customers, accounts = generate_customer_data()
    assert len(customers) == NUM_CUSTOMERS
    assert len(accounts) >= NUM_CUSTOMERS


def test_customer_fields_present():
    customers, _ = generate_customer_data()
    sample = customers[0]
    assert "email" in sample
    assert "cpf" in sample
    assert "risk_profile" in sample
