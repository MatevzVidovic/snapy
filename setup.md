


poetry add syrupy




def test_function_output(snapshot):
    result = your_function()
    assert result == snapshot



# Running tests

# First run creates snapshots
pytest test_file.py

# Update snapshots when behavior changes
pytest test_file.py --snapshot-update

# Show snapshot details
pytest test_file.py -v







# Key features

# Filter dynamic data
def test_api_response(snapshot):
    response = api_call()
    assert response == snapshot(exclude=['timestamp', 'id'])

# Named snapshots
def test_multiple_scenarios(snapshot):
    result1 = function(scenario1)
    assert result1 == snapshot(name='scenario_1')
    
    result2 = function(scenario2)
    assert result2 == snapshot(name='scenario_2')

# Custom matchers
def test_with_custom_filtering(snapshot):
    data = {'user_id': 123, 'created_at': '2023-01-01', 'name': 'John'}
    assert data == snapshot(matcher=path_type({'created_at': (str,)}))