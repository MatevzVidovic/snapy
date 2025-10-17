


python3 -m examples.basics

poetry run pytest --envfile=.env -vv --capture=tee-sys

poetry run pytest --envfile=.env --snapshot-update



poetry run pytest --envfile=.env -k _DI -vv --capture=tee-sys

poetry run pytest --envfile=.env -k _DI --snapshot-update


# Near plan

- make snapy a real module, with __init__.py. Make examples be tests for it, where also the behaviour is showcased.
- rename this README.md into WORKING.md
- make use docs in  README.md   (the 3 features, how to use each feature - explanation of how it works is to ctrl+F some fn that has great comments that explain it all)
- figure out the symrepo approach and put the instructions for setting it up in __init__.py

- create a plantUML function call graph, where each fn gets its own box, and has arrows to other fns it uses. Have the arrows be numbered at the stem (sequence number of which fn it is in the original fn implementation)

- make sure everything now works correctly