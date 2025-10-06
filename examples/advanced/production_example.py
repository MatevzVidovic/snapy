"""
Production usage example showing best practices for using snapy_capture in production environments.

This example demonstrates:
1. Production-safe configuration
2. Performance monitoring
3. Minimal capture mode
4. Error handling and recovery
"""

import os
from snapy.capture import capture_args, CaptureContext, capture_minimal
from snapy.capture.config import CaptureConfig, set_global_config
from snapy.capture.performance import (
    configure_for_production,
    get_performance_monitor,
    print_performance_report,
    performance_context
)


# Configure for production environment
def setup_production_config():
    """Set up production-safe configuration."""
    # Set environment variables for production
    os.environ['SNAP_CAPTURE_PRODUCTION_MODE'] = 'true'
    os.environ['SNAP_CAPTURE_MINIMAL'] = 'true'
    os.environ['SNAP_CAPTURE_DEFAULT_RETENTION'] = '1'  # Keep only latest
    os.environ['SNAP_CAPTURE_IGNORE_ARGS'] = 'password,token,secret,api_key,private_key'

    # Create production config
    config = CaptureConfig()
    config.production_mode = True
    config.minimal_capture = True
    config.default_retention = 1

    # Set global config
    set_global_config(config)

    # Apply production optimizations
    configure_for_production()

    print("✓ Production configuration applied")


@capture_args()
def critical_business_function(transaction_id: str, amount: float, account_data: dict):
    """
    Critical business function that processes financial transactions.

    In production, this captures minimal argument information for debugging
    while filtering sensitive data.
    """
    # Validate inputs
    if not transaction_id:
        raise ValueError("Transaction ID is required")

    if amount <= 0:
        raise ValueError("Amount must be positive")

    if not account_data.get('account_number'):
        raise ValueError("Account number is required")

    # Simulate complex business logic
    processed_transaction = {
        "transaction_id": transaction_id,
        "amount": amount,
        "status": "processed",
        "account_type": account_data.get("type", "standard"),
        "fees": calculate_fees(amount, account_data.get("type", "standard"))
    }

    # Log successful processing
    audit_log(transaction_id, "SUCCESS", processed_transaction)

    return processed_transaction


@capture_minimal()
def high_frequency_function(data_batch: list, processing_options: dict):
    """
    High-frequency function that uses minimal capture to reduce overhead.

    This function is called thousands of times per minute, so we use
    minimal capture to avoid performance impact.
    """
    processed_count = 0
    errors = []

    for item in data_batch:
        try:
            process_single_item(item, processing_options)
            processed_count += 1
        except Exception as e:
            errors.append(str(e))

    return {
        "processed": processed_count,
        "errors": len(errors),
        "error_details": errors[:5]  # Limit error details
    }


def calculate_fees(amount: float, account_type: str) -> float:
    """Calculate transaction fees based on amount and account type."""
    fee_rates = {
        "premium": 0.01,
        "standard": 0.02,
        "basic": 0.03
    }

    base_rate = fee_rates.get(account_type, 0.02)
    return round(amount * base_rate, 2)


def process_single_item(item: dict, options: dict):
    """Process a single data item."""
    if not item.get("id"):
        raise ValueError("Item ID is required")

    # Simulate processing
    return {"id": item["id"], "processed": True}


def audit_log(transaction_id: str, status: str, details: dict):
    """Log transaction for audit purposes."""
    print(f"AUDIT: {transaction_id} - {status} - {details}")


def demonstrate_production_patterns():
    """Demonstrate production usage patterns."""
    print("Demonstrating production patterns...")

    # Pattern 1: Selective capture for critical functions
    print("\n1. Critical function with full capture:")
    try:
        result = critical_business_function(
            transaction_id="TXN001",
            amount=1000.50,
            account_data={
                "account_number": "1234567890",
                "type": "premium",
                "secret_key": "very_secret"  # This will be filtered
            }
        )
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")

    # Pattern 2: Minimal capture for high-frequency functions
    print("\n2. High-frequency function with minimal capture:")
    data_batch = [
        {"id": "item1", "value": 100},
        {"id": "item2", "value": 200},
        {"id": "item3"},  # Missing value - will cause error
        {"id": "item4", "value": 400}
    ]

    result = high_frequency_function(data_batch, {"validate": True})
    print(f"   Result: {result}")

    # Pattern 3: Conditional capture based on environment
    print("\n3. Environment-based capture:")
    with CaptureContext(enabled=os.getenv('DEBUG_MODE') == 'true'):
        # This will only capture if DEBUG_MODE=true
        debug_result = critical_business_function(
            "DEBUG_TXN",
            50.00,
            {"account_number": "DEBUG123", "type": "standard"}
        )
        print(f"   Debug result: {debug_result}")


def demonstrate_performance_monitoring():
    """Demonstrate performance monitoring in production."""
    print("\n" + "="*50)
    print("PERFORMANCE MONITORING DEMONSTRATION")
    print("="*50)

    with performance_context():
        # Simulate production workload
        print("\nSimulating production workload...")

        for i in range(10):
            # Critical transactions
            critical_business_function(
                f"TXN{i:03d}",
                100.0 + i * 10,
                {"account_number": f"ACC{i:06d}", "type": "standard"}
            )

        # High-frequency processing
        for batch_num in range(5):
            batch = [{"id": f"item_{batch_num}_{i}", "value": i * 10} for i in range(20)]
            high_frequency_function(batch, {"validate": True})

    # Print performance report
    print("\nPerformance Report:")
    print_performance_report()


def demonstrate_error_recovery():
    """Demonstrate error handling and recovery patterns."""
    print("\n" + "="*50)
    print("ERROR HANDLING DEMONSTRATION")
    print("="*50)

    # Pattern 1: Graceful degradation when capture fails
    print("\n1. Graceful degradation:")

    @capture_args(path="/invalid/path/that/does/not/exist")
    def function_with_bad_path(data):
        """Function with invalid capture path - should still work."""
        return f"Processed: {data}"

    result = function_with_bad_path("test_data")
    print(f"   Function result: {result}")
    print("   ✓ Function worked despite capture failure")

    # Pattern 2: Capture with unpickleable objects
    print("\n2. Handling unpickleable objects:")

    @capture_args()
    def function_with_unpickleable(func, data):
        """Function that receives unpickleable lambda function."""
        return func(data)

    try:
        result = function_with_unpickleable(lambda x: x.upper(), "hello")
        print(f"   Function result: {result}")
        print("   ✓ Function worked with unpickleable arguments")
    except Exception as e:
        print(f"   Error: {e}")

    # Pattern 3: Recovery from storage issues
    print("\n3. Storage issue recovery:")
    from snapy.capture import CaptureLoader

    # Try to load from non-existent path
    loader = CaptureLoader("/completely/invalid/path")
    functions = loader.list_functions()
    print(f"   Functions from invalid path: {functions}")
    print("   ✓ Loader handled invalid path gracefully")


def production_best_practices():
    """Show production best practices."""
    print("\n" + "="*50)
    print("PRODUCTION BEST PRACTICES")
    print("="*50)

    print("\n1. Configuration Management:")
    print("   ✓ Use environment variables for configuration")
    print("   ✓ Enable production mode in production environments")
    print("   ✓ Use minimal capture for high-frequency functions")
    print("   ✓ Set appropriate retention policies")

    print("\n2. Security:")
    print("   ✓ Filter sensitive arguments (passwords, tokens, keys)")
    print("   ✓ Use custom ignore patterns for your domain")
    print("   ✓ Review captured data regularly")

    print("\n3. Performance:")
    print("   ✓ Monitor capture overhead with performance tools")
    print("   ✓ Use conditional capture based on environment")
    print("   ✓ Implement graceful degradation")

    print("\n4. Monitoring:")
    print("   ✓ Track capture success/failure rates")
    print("   ✓ Monitor storage usage")
    print("   ✓ Set up alerts for capture failures")

    print("\n5. Testing:")
    print("   ✓ Test with captured production arguments")
    print("   ✓ Combine with trace testing for comprehensive coverage")
    print("   ✓ Validate capture/replay consistency")


def main():
    """Main demonstration function."""
    print("SNAPY CAPTURE - PRODUCTION EXAMPLE")
    print("="*60)

    # Setup production configuration
    setup_production_config()

    # Demonstrate patterns
    demonstrate_production_patterns()

    # Show performance monitoring
    demonstrate_performance_monitoring()

    # Show error handling
    demonstrate_error_recovery()

    # Show best practices
    production_best_practices()

    print("\n" + "="*60)
    print("✓ Production example completed!")
    print("\nKey takeaways:")
    print("- snapy_capture is safe for production use with proper configuration")
    print("- Performance impact is minimal with production optimizations")
    print("- Captured arguments enable powerful testing with real data")
    print("- Error handling ensures graceful degradation")


if __name__ == "__main__":
    main()