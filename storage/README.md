# Local Storage

This directory holds locally stored files for development, including:

- **Curriculum uploads** — files uploaded through the Content Factory

## Structure

```
storage/
└── curriculum/
    └── {course_id}/
        └── {unit_id}/
            └── {lesson_id}/
                └── original-file-name.ext
```

## Configuration

The storage root is configured via the `STORAGE_ROOT` environment variable
in `backend/.env`. The default value is `../storage`, which resolves to
this directory relative to `backend/`.

## Production

In production, local storage is replaced by a cloud storage provider
(S3, Cloudflare R2, Supabase Storage, or MinIO). The backend uses a
`StorageProvider` abstraction so the switch requires no changes to
lesson or curriculum logic.

## Git

This directory is excluded from Git via `.gitignore`. Do not commit
uploaded files.
