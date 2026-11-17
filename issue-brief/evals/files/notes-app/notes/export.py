"""CSV export of every note in a store."""

import csv
import io

from notes.store import NoteStore

EXPORT_COLUMNS = ["id", "title", "body"]


def export_csv(store: NoteStore) -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(EXPORT_COLUMNS)
    for note in store.all_notes():
        writer.writerow([note.id, note.title, note.body])
    return out.getvalue()
