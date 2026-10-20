from glitch_runner.presentation.renderer import _music_status


def test_music_status_is_on_while_music_plays(session):
    assert _music_status(session) == "ON"


def test_music_status_is_muted_after_toggling(session):
    session.toggle_music()
    assert _music_status(session) == "MUTED"
