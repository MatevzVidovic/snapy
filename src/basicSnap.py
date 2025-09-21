




def test_snap_outer(snapshot):
    from basicExample import outer
    snapshot.assert_match(outer("ena", "dva"))