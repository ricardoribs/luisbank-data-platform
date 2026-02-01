from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import random

# Enum para status da conta
from enum import Enum

class AccountType(str, Enum):
    CHECKING = "CHECKING"  # Corrente
    SAVINGS = "SAVINGS"    # Poupança
    SALARY = "SALARY"      # Salário

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    first_name: str
    last_name: str
    email: EmailStr
    cpf: str
    created_at: datetime
    updated_at: datetime
    # Categoria de Risco (A, B, C) - Útil para Analytics de Risco depois
    risk_profile: str 

class Account(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    customer_id: str  # Foreign Key para o Cliente
    account_number: str
    agency: str = "0001"
    balance: float  # Saldo inicial (ledger snapshot)
    account_type: AccountType
    created_at: datetime
    status: str = "ACTIVE"

class TransactionType(str, Enum):
    PIX_IN = "PIX_IN"        # Recebeu Pix
    PIX_OUT = "PIX_OUT"      # Enviou Pix
    TED_IN = "TED_IN"
    TED_OUT = "TED_OUT"
    BOLETO_PAY = "BOLETO_PAY" # Pagou boleto

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    account_id: str  # Quem originou o evento no nosso banco
    amount: float
    transaction_type: TransactionType
    transaction_date: datetime
    status: str = "COMPLETED"
    # Campos extras para enriquecer analytics
    counterparty_bank: str = "INTERNAL" # Se for outro banco, geramos nome aleatório