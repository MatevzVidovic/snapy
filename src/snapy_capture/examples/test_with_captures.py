"""
Example test file showing how to use captured arguments in tests.

This demonstrates how to load and replay captured function arguments
in your test suite using pytest and syrupy.
"""

import pytest
from snapy_capture import load_capture, load_all_captures, has_capture, CaptureLoader
from .basic_usage import process_user_data, api_request, calculate_metrics


class TestWithCapturedArguments:
    """Test class using captured arguments."""

    def test_process_user_data_with_captured_args(self, snapshot):
        """Test using the latest captured arguments."""
        if not has_capture("process_user_data"):
            pytest.skip("No captured arguments found for process_user_data")

        # Load the most recent captured arguments
        args, kwargs = load_capture("process_user_data")

        # Replay the function call
        result = process_user_data(*args, **kwargs)

        # Use snapshot testing to verify the result
        assert result == snapshot

    def test_process_user_data_all_captures(self, snapshot):
        """Test all captured argument combinations."""
        loader = CaptureLoader()

        if not loader.has_captures("process_user_data"):
            pytest.skip("No captured arguments found for process_user_data")

        all_captures = loader.load_all("process_user_data")
        results = []

        for args, kwargs in all_captures:
            result = process_user_data(*args, **kwargs)
            results.append(result)

        # Snapshot test all results
        assert results == snapshot

    def test_api_request_with_manual_args(self, snapshot):
        """Test with manually created arguments when no captures exist."""
        try:
            # Try to load captured arguments first
            args, kwargs = load_capture("api_request")
        except (TypeError, ValueError):
            # Fall back to manual arguments if no captures
            args = ("/test/endpoint",)
            kwargs = {
                "params": {"test": "value"},
                "api_key": "test_key_123"
            }

        result = api_request(*args, **kwargs)
        assert result == snapshot

    def test_calculate_metrics_parametrized(self, snapshot):
        """Test using captured arguments with different methods."""
        loader = CaptureLoader("./special_captures")  # Custom path

        if not loader.has_captures("calculate_metrics"):
            pytest.skip("No captured arguments found for calculate_metrics")

        all_captures = loader.load_all("calculate_metrics")
        results = {}

        for i, (args, kwargs) in enumerate(all_captures):
            result = calculate_metrics(*args, **kwargs)
            results[f"capture_{i}"] = result

        assert results == snapshot

    def test_with_capture_metadata(self):
        """Test accessing capture metadata."""
        loader = CaptureLoader()

        if not loader.has_captures("process_user_data"):
            pytest.skip("No captured arguments found")

        capture = loader.load_capture_object("process_user_data")

        # Verify metadata
        assert capture.metadata.function_name == "process_user_data"
        assert capture.metadata.args_count >= 2  # user_id and data
        assert isinstance(capture.metadata.timestamp, type(capture.metadata.timestamp))

        # Use the captured arguments
        result = process_user_data(*capture.args, **capture.kwargs)
        assert result is not None


class TestCaptureFixtures:
    """Test using pytest fixtures with captures."""

    @pytest.fixture
    def user_data_capture(self):
        """Fixture that loads user data captures."""
        if not has_capture("process_user_data"):
            pytest.skip("No captured arguments found")
        return load_capture("process_user_data")

    @pytest.fixture
    def api_request_captures(self):
        """Fixture that loads all API request captures."""
        loader = CaptureLoader()
        if not loader.has_captures("api_request"):
            pytest.skip("No captured arguments found")
        return loader.load_all("api_request")

    def test_with_user_data_fixture(self, user_data_capture, snapshot):
        """Test using user data fixture."""
        args, kwargs = user_data_capture
        result = process_user_data(*args, **kwargs)
        assert result == snapshot

    def test_with_api_request_fixture(self, api_request_captures, snapshot):
        """Test using API request fixture with multiple captures."""
        results = []
        for args, kwargs in api_request_captures:
            result = api_request(*args, **kwargs)
            results.append(result)

        assert results == snapshot


@pytest.mark.parametrize("capture_index", [0, 1, 2])
def test_calculate_metrics_by_index(capture_index, snapshot):
    """Parametrized test using different capture indices."""
    loader = CaptureLoader("./special_captures")

    if loader.get_capture_count("calculate_metrics") <= capture_index:
        pytest.skip(f"Not enough captures (need index {capture_index})")

    args, kwargs = loader.load_by_index("calculate_metrics", capture_index)
    result = calculate_metrics(*args, **kwargs)

    assert result == snapshot


class TestCaptureIntegration:
    """Integration tests for capture functionality."""

    def test_capture_and_replay_workflow(self):
        """Test complete capture and replay workflow."""
        from snapy_capture import capture_args

        @capture_args(path="./test_captures")
        def temp_function(x, y, operation="add"):
            operations = {
                "add": lambda a, b: a + b,
                "multiply": lambda a, b: a * b,
                "subtract": lambda a, b: a - b
            }
            return operations.get(operation, lambda a, b: 0)(x, y)

        # Generate captures
        original_results = []
        test_cases = [
            (5, 3, "add"),
            (4, 6, "multiply"),
            (10, 2, "subtract")
        ]

        for x, y, op in test_cases:
            result = temp_function(x, y, operation=op)
            original_results.append(result)

        # Load and replay captures
        loader = CaptureLoader("./test_captures")
        captures = loader.load_all("temp_function")

        replayed_results = []
        for args, kwargs in captures:
            result = temp_function(*args, **kwargs)
            replayed_results.append(result)

        # Results should match
        assert len(original_results) == len(replayed_results)
        assert sorted(original_results) == sorted(replayed_results)

    def test_error_handling_with_captures(self):
        """Test error handling when loading captures."""
        loader = CaptureLoader("./nonexistent_path")

        # Should handle non-existent paths gracefully
        functions = loader.list_functions()
        assert functions == []

        # Should handle non-existent functions gracefully
        result = loader.load_latest("nonexistent_function")
        assert result is None

    def test_capture_statistics(self):
        """Test getting capture statistics."""
        loader = CaptureLoader()
        stats = loader.get_storage_stats()

        assert "total_functions" in stats
        assert "total_files" in stats
        assert "function_stats" in stats
        assert isinstance(stats["total_functions"], int)


if __name__ == "__main__":
    # Run examples first to generate captures
    print("Generating example captures...")
    from .basic_usage import run_examples
    run_examples()

    print("\nRunning tests with captured arguments...")
    pytest.main([__file__, "-v"])