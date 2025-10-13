


python3 -m examples.basics

poetry run pytest --envfile=.env -vv --capture=tee-sys

poetry run pytest --envfile=.env --snapshot-update



poetry run pytest --envfile=.env -k _DI -vv --capture=tee-sys

poetry run pytest --envfile=.env -k _DI --snapshot-update


# Near plan

- remove load_all  - get blob paths + get blob is the idiomatic way.

- (hopefully works) side effect lookup make env var a default param
- side_effect_lookup and onward has to have comments checked and made

- make comments for every fn in capture.py , explaining what is its purpose, and how it does it. Also giving inline comments for what sections of code do. The goal is to have as little text as possible - be very bulletpoint oriented and concise.
- create a plantUML function graph, where each fn gets its own box, and has arrows to other fns it uses. Have the arrows be numbered at the stem (sequence number of which fn it is in the original fn implementation)
- make capture a real module, with __init__.py. Make examples be tests for it, where also the behaviour is showcased.
- make an API spec of the capture module - put it into __init__.py
- add pylint and mypy and make them work well
- make a makefile with the pytest commands and such

- make sure everything now works correctly