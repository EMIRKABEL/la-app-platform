"""Enums used across models."""

import enum


class LessonStatus(enum.Enum):
    """Lifecycle status for a Lesson."""

    draft = "draft"
    analyzing = "analyzing"
    review = "review"
    approved = "approved"
    published = "published"


class ActivityStatus(enum.Enum):
    """Lifecycle status for an Activity."""

    draft = "draft"
    review = "review"
    approved = "approved"
    published = "published"


class CurriculumProcessingStatus(enum.Enum):
    """Processing status for an uploaded curriculum source."""

    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class AssetApprovalStatus(enum.Enum):
    """Approval status for an asset."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class LessonVersionStatus(enum.Enum):
    """Status for a lesson version snapshot."""

    draft = "draft"
    published = "published"
    archived = "archived"
