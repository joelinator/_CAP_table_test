import pytest
from unittest.mock import Mock, patch
from app.domain.use_cases import CreateShareholder, CreateIssuance
from app.domain.entities import User, Role, Shareholder, ShareIssuance, AuditEvent

@pytest.fixture
def mock_repos():
    user_repo = Mock()
    shareholder_repo = Mock()
    audit_repo = Mock()
    return user_repo, shareholder_repo, audit_repo

@pytest.fixture
def mock_admin_user():
    return User(id=1, username="admin", password_hash="hashed", role=Role.ADMIN)

@pytest.fixture(autouse=True)
def mock_cache():
    with patch("app.infrastructure.cache.delete_cache") as mock:
        mock.side_effect = lambda *args: None
        yield

def test_create_shareholder_success(mock_repos, mock_admin_user):
    user_repo, shareholder_repo, audit_repo = mock_repos
    use_case = CreateShareholder(user_repo, shareholder_repo, audit_repo)
    user_repo.get_by_username.return_value = None
    shareholder_repo.get_by_email.return_value = None
    user_repo.create.return_value = User(id=2, username="johndoe", password_hash="hashed", role=Role.SHAREHOLDER)
    shareholder_repo.create.return_value = Shareholder(user_id=2, name="John Doe", email="john@example.com")

    result = use_case.execute("John Doe", "john@example.com", "johndoe", "password123", mock_admin_user)
    assert isinstance(result, Shareholder)
    assert result.user_id == 2
    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    user_repo.create.assert_called_once()
    shareholder_repo.create.assert_called_once()
    audit_repo.create.assert_called_once()

def test_create_issuance_validation():
    iss_repo = Mock()
    sh_repo = Mock()
    audit_repo = Mock()
    sh_repo.get_by_id.return_value = Mock(id=1)
    use_case = CreateIssuance(iss_repo, sh_repo, audit_repo)
    admin = User(id=1, username="admin", password_hash="", role=Role.ADMIN)
    
    with pytest.raises(ValueError):
        use_case.execute(1, -5, 10.0, admin)  # Negative shares
    
    with pytest.raises(ValueError):
        sh_repo.get_by_id.return_value = None
        use_case.execute(999, 10, 10.0, admin)  # Non-existent shareholder
    
    with pytest.raises(PermissionError):
        use_case.execute(1, 10, 10.0, User(id=2, username="sh", password_hash="", role=Role.SHAREHOLDER))  # Not admin

def test_create_issuance_success(mock_repos, mock_admin_user):
    _, shareholder_repo, audit_repo = mock_repos
    issuance_repo = Mock()
    use_case = CreateIssuance(issuance_repo, shareholder_repo, audit_repo)
    shareholder_repo.get_by_id.return_value = Mock(id=1)
    issuance_repo.create.return_value = ShareIssuance(id=1, shareholder_id=1, number_of_shares=100,price=10.0)
    result = use_case.execute(1, 100, 10.0, mock_admin_user)
    assert isinstance(result, ShareIssuance)
    assert result.number_of_shares == 100
    issuance_repo.create.assert_called_once()
    audit_repo.create.assert_called_once()
