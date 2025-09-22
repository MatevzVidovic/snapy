
How does pysnap work?

Snap testing works like this:
def test_sthsth(snapshot):
    you run your, code, whatever
    result = whatever you include in the result
    assert result == snapshot

You use a testing lib, like pytest. It autopmatically detects tests with snapshot in them.
And detects where the assert takes place.
You then run it with --update-snapshots and it saves the result (that which is compared to snapshot) to a file in whatever way.

In the most basic form, you are testing some fn, and all you can snapshot is the result (and possibly the args, but you set those manually in the test anyway).
You dont have access to the inside of the fn.

All that we do now, is:
we set a context (the with sthsth:)
This sets a tracer (see below)
Whenever there is a call, we save the args, and whenever there is a return line, we save the return.
We then serialize all of these args, and we compare all of this to the snapshot (all of this is the snapshot).
This way, we have much more control over everything.

And that is basically it.

It utilizes a tracer: the sys lib can have some fn set, which it excecutes before every line. It says if the curr line is a call, enter (for enterig contexts), return, or line (for basic lines). And it gives you the current frame (fn frame with args and locals).
This is used by debuggers, coverage monitors (which lines were run) etc.

