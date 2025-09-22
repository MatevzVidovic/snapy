"""
Basic usage examples for snapy_capture.

This module demonstrates how to use the @capture_args decorator
to automatically capture function arguments for replay in tests.
"""

from snapy_capture import capture_args


@capture_args()
def process_user_data(user_id: str, data: dict, validate: bool = True):
    """
    Example function that processes user data.

    Arguments are automatically captured when this function is called.
    """
    if validate:
        if not user_id or not isinstance(data, dict):
            raise ValueError("Invalid input data")

    processed = {
        "user_id": user_id,
        "data_keys": list(data.keys()),
        "data_count": len(data),
        "processed_at": "2023-01-01T00:00:00Z"
    }

    return processed


@capture_args(retention=3, ignore_args=["api_key"])
def api_request(endpoint: str, params: dict, api_key: str = None):
    """
    Example API request function with custom capture settings.

    - Keeps last 3 captures (retention=3)
    - Filters out api_key from captured arguments for security
    """
    # Simulate API request
    if not api_key:
        raise ValueError("API key required")

    response = {
        "endpoint": endpoint,
        "params": params,
        "status": "success",
        "data": f"Response from {endpoint}"
    }

    return response


@capture_args(path="./special_captures")
def calculate_metrics(data: list, method: str = "average"):
    """
    Example function with custom storage path.

    Captures are stored in './special_captures' directory.
    """
    if method == "average":
        return sum(data) / len(data) if data else 0
    elif method == "sum":
        return sum(data)
    elif method == "max":
        return max(data) if data else None
    else:
        raise ValueError(f"Unknown method: {method}")


def run_examples():
    """Run the example functions to generate captures."""
    print("Running snapy_capture examples...")

    # Example 1: Basic usage
    print("\n1. Basic user data processing:")
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    }
    result1 = process_user_data("user123", user_data)
    print(f"Result: {result1}")

    # Example 2: API request with sensitive data filtering
    print("\n2. API request (api_key will be filtered):")
    try:
        result2 = api_request(
            endpoint="/users",
            params={"limit": 10, "offset": 0},
            api_key="secret_key_123"
        )
        print(f"Result: {result2}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Multiple calls to show retention policy
    print("\n3. Multiple API calls (testing retention=3):")
    for i in range(5):
        api_request(
            endpoint=f"/data/{i}",
            params={"page": i},
            api_key="secret_key_123"
        )
        print(f"  Call {i+1} completed")

    # Example 4: Custom storage path
    print("\n4. Metrics calculation with custom storage:")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    avg_result = calculate_metrics(numbers, "average")
    sum_result = calculate_metrics(numbers, "sum")
    max_result = calculate_metrics(numbers, "max")

    print(f"Average: {avg_result}")
    print(f"Sum: {sum_result}")
    print(f"Max: {max_result}")

    print("\n✓ Examples completed! Check the capture directories for saved arguments.")
    print("  - Default captures: ./snap_capture/")
    print("  - Special captures: ./special_captures/")


if __name__ == "__main__":
    run_examples()