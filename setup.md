


poetry add syrupy




def test_function_output(snapshot):
    result = your_function()
    assert result == snapshot



# Running tests

# First run creates snapshots
pytest test_file.py

# Update snapshots when behavior changes
pytest --snapshot-update
pytest test_file.py --snapshot-update

# Show snapshot details
pytest test_file.py -v




