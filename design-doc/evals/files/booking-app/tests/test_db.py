import unittest

from booking import db


class SlotTests(unittest.TestCase):
    def test_add_slot(self):
        conn = db.connect()
        slot_id = db.add_slot(conn, "oslo", "2026-11-02T06:00:00Z", 12)
        row = conn.execute("SELECT * FROM class_slot WHERE id = ?", (slot_id,)).fetchone()
        self.assertEqual(row["capacity"], 12)


if __name__ == "__main__":
    unittest.main()
