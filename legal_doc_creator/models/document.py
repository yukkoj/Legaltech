"""Data models for legal documents."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class DocumentRevision:
    """Represents a single revision of a document."""
    version: int
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    agent_type: str = ""  # 'draft' or 'edit'
    feedback: Optional[str] = None


@dataclass
class LegalDocument:
    """Main legal document model."""
    id: str
    document_type: str
    requirements: str
    initial_content: str = ""
    
    revisions: list[DocumentRevision] = field(default_factory=list)
    current_version: int = 0
    status: str = "pending"  # pending, drafting, editing, completed
    
    def add_revision(self, content: str, agent_type: str, feedback: Optional[str] = None):
        """Add a new revision to the document."""
        revision = DocumentRevision(
            version=self.current_version + 1,
            content=content,
            agent_type=agent_type,
            feedback=feedback
        )
        self.revisions.append(revision)
        self.current_version += 1
        return revision
    
    def get_current_content(self) -> str:
        """Get the current version of the document."""
        if self.revisions:
            return self.revisions[-1].content
        return self.initial_content
    
    def get_history(self) -> list[dict]:
        """Get revision history."""
        return [
            {
                "version": r.version,
                "agent": r.agent_type,
                "timestamp": r.timestamp.isoformat(),
                "feedback": r.feedback
            }
            for r in self.revisions
        ]
