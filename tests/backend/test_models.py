from __future__ import annotations

from sqlalchemy import JSON, select
from sqlalchemy.orm import configure_mappers

from backend.core.config import Settings, settings
from backend.core.database import Base, SessionLocal, engine
from backend.models import AIAnalysis, Case, CaseEvidence, Donation, Donor, Flag, User


def test_configuration_does_not_require_openai_key() -> None:

	assert "OPENAI_API_KEY" not in Settings.model_fields
	assert settings.OLLAMA_BASE_URL == "http://localhost:11434"
	assert settings.OLLAMA_MODEL == "qwen3:4b"


def test_database_engine_and_session_initialize() -> None:
	session = SessionLocal()
	try:
		assert engine is not None
		assert session.bind is engine
	finally:
		session.close()


def test_all_models_register_expected_metadata() -> None:
	configure_mappers()
	assert {
		"users",
		"cases",
		"donors",
		"donations",
		"case_evidence_manifest",
		"ai_analyses",
		"flags",
	}.issubset(Base.metadata.tables)
	assert User.__tablename__ == "users"
	assert AIAnalysis.__tablename__ == "ai_analyses"
	assert Flag.__tablename__ == "flags"


def test_existing_table_mappings_preserve_names_and_json_types() -> None:
	assert Case.__tablename__ == "cases"
	assert Donation.__tablename__ == "donations"
	assert Donor.__tablename__ == "donors"
	assert CaseEvidence.__tablename__ == "case_evidence_manifest"
	assert isinstance(Case.__table__.c.latitude.type, JSON)
	assert isinstance(Case.__table__.c.longitude.type, JSON)
	assert isinstance(Case.__table__.c.estimated_funding.type, JSON)
	assert isinstance(Case.__table__.c.current_funding.type, JSON)
	assert isinstance(Donor.__table__.c.budget.type, JSON)
	assert isinstance(Donation.__table__.c.amount.type, JSON)


def test_relationships_are_configured() -> None:
	configure_mappers()
	assert set(Donation.__mapper__.relationships.keys()) == {"case", "donor", "user"}
	assert set(Case.__mapper__.relationships.keys()) == {"donations", "evidence", "analyses", "flags", "creator"}
	assert set(Donor.__mapper__.relationships.keys()) == {"donations"}
	assert set(CaseEvidence.__mapper__.relationships.keys()) == {"case"}


def test_existing_neon_rows_and_relationships_are_readable() -> None:
	with SessionLocal() as session:
		case = session.scalars(select(Case).order_by(Case.case_id).limit(1)).first()
		donor = session.scalars(select(Donor).order_by(Donor.donor_id).limit(1)).first()
		donation = session.scalars(select(Donation).order_by(Donation.donation_id).limit(1)).first()

		assert case is not None
		assert donor is not None
		assert donation is not None
		assert donation.case is not None
		assert donation.donor is not None
		assert donation.case.case_id == donation.case_id
		assert donation.donor.donor_id == donation.donor_id
