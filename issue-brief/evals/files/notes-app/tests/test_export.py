from notes.export import export_csv
from notes.store import NoteStore


def test_export_has_header_and_one_row_per_note():
    store = NoteStore()
    store.save_note("Groceries", "milk, eggs", tags=["home"])
    store.save_note("Standup", "ship export")
    lines = export_csv(store).strip().splitlines()
    assert lines[0] == "id,title,body"
    assert len(lines) == 3
