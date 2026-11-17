"""In-memory note store. Notes live only in this process."""

from __future__ import annotations

from dataclasses import dataclass, field

MAX_NOTE_CHARS = 2000


@dataclass
class Note:
    id: int
    title: str
    body: str
    tags: list[str] = field(default_factory=list)


class NoteStore:
    def __init__(self) -> None:
        self._notes: dict[int, Note] = {}
        self._next_id = 1

    def save_note(self, title: str, body: str, tags: list[str] | None = None) -> Note:
        if len(body) > MAX_NOTE_CHARS:
            raise ValueError(f"note body is over {MAX_NOTE_CHARS} characters")
        note = Note(self._next_id, title, body, list(tags or []))
        self._notes[note.id] = note
        self._next_id += 1
        return note

    def all_notes(self) -> list[Note]:
        return sorted(self._notes.values(), key=lambda note: note.id)
