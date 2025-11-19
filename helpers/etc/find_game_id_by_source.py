from typing import Optional

def _find_game_id_by_source(cur, source_game_id: int) -> Optional[int]:
    if not source_game_id:
        return None
    cur.execute("SELECT id FROM games WHERE source_game_id = %s", (source_game_id,))
    r = cur.fetchone()
    return r[0] if r else None