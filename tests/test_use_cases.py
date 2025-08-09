# tests/test_use_cases.py
# Example unit test
import pytest
from app.domain.use_cases import CreateIssuance
from app.domain.entities import User, Role
from unittest.mock import MagicMock

def test_create_issuance_validation():
    iss_repo = MagicMock()
    sh_repo = MagicMock()
    audit_repo = MagicMock()
    sh_repo.get_by_id.return_value = MagicMock(id=1)
    use_case = CreateIssuance(iss_repo, sh_repo, audit_repo)
    admin = User(id=1, username="admin", password_hash="", role=Role.ADMIN)
    
    with pytest.raises(ValueError):
        use_case.execute(1, -5, 10.0, admin)  # Negative shares
    
    with pytest.raises(ValueError):
        sh_repo.get_by_id.return_value = None
        use_case.execute(999, 10, 10.0, admin)  # Non-existent shareholder
    
    with pytest.raises(PermissionError):
        use_case.execute(1, 10, 10.0, User(id=2, username="sh", password_hash="", role=Role.SHAREHOLDER))  # Not admin
