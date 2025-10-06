#!/usr/bin/env python3
"""
Example showing how to filter out large arguments using the new named argument format.

This demonstrates the key benefit: capturing arguments with their names in an ordered
dictionary, allowing easy filtering of large arguments while maintaining order.
"""

from snapy.capture import capture_args, load_capture_dict


@capture_args()
def train_ml_model(data: list, model_weights: dict, hyperparams: dict, large_embeddings=None):
    """
    Example ML training function with potentially large arguments.

    - data: Training data (could be large)
    - model_weights: Pre-trained model weights (could be very large)
    - hyperparams: Training hyperparameters (small)
    - large_embeddings: Word embeddings (could be massive)
    """
    print(f"Training with {len(data)} samples")
    print(f"Model has {len(model_weights)} weight tensors")
    print(f"Hyperparams: {hyperparams}")
    print(f"Using embeddings: {large_embeddings is not None}")

    # Simulate training
    return {
        "loss": 0.123,
        "accuracy": 0.95,
        "model_size": len(model_weights),
        "data_points": len(data)
    }


def demonstrate_filtering():
    """Demonstrate filtering large arguments in tests."""
    print("=== Capturing ML Function Call ===")

    # Simulate function call with large data
    result = train_ml_model(
        data=list(range(10000)),  # Large training data
        model_weights={f"layer_{i}": f"weights_{i}" for i in range(100)},  # Large model
        hyperparams={"lr": 0.001, "batch_size": 32, "epochs": 100},  # Small config
        large_embeddings={f"word_{i}": f"embedding_{i}" for i in range(50000)}  # Huge embeddings
    )
    print(f"Training result: {result}\n")

    print("=== Loading Captured Arguments ===")

    # Load the captured arguments as dictionary
    args_dict = load_capture_dict("train_ml_model")

    print("Captured argument names and sizes:")
    for name, value in args_dict.items():
        if hasattr(value, '__len__'):
            print(f"  {name}: {type(value).__name__} with {len(value)} items")
        else:
            print(f"  {name}: {type(value).__name__} = {value}")

    print(f"\nArgument order: {list(args_dict.keys())}")

    print("\n=== Testing Scenarios ===")

    # Scenario 1: Use all arguments (might be slow/memory intensive)
    print("\n1. Full replay with all arguments:")
    print("   train_ml_model(*args_dict.values())")
    print("   -> This would use all large data, might be slow")

    # Scenario 2: Filter out large arguments for fast testing
    print("\n2. Filter out large arguments for fast testing:")
    fast_test_args = {
        k: v for k, v in args_dict.items()
        if k not in ['large_embeddings', 'data']
    }
    print(f"   Filtered args: {list(fast_test_args.keys())}")

    # Use smaller test data
    fast_test_args['data'] = [1, 2, 3]  # Small test data

    fast_result = train_ml_model(**fast_test_args)
    print(f"   Fast test result: {fast_result}")

    # Scenario 3: Keep model weights but use small test data
    print("\n3. Keep model but use small test data:")
    model_test_args = {
        k: v for k, v in args_dict.items()
        if k != 'large_embeddings'
    }
    model_test_args['data'] = [1, 2, 3, 4, 5]  # Small test dataset

    print(f"   Args: {list(model_test_args.keys())}")
    model_result = train_ml_model(**model_test_args)
    print(f"   Model test result: {model_result}")

    # Scenario 4: Test different hyperparameters
    print("\n4. Test with different hyperparameters:")
    hyper_test_args = args_dict.copy()
    hyper_test_args['hyperparams'] = {"lr": 0.01, "batch_size": 64, "epochs": 50}
    hyper_test_args['data'] = [1, 2, 3]  # Small data for testing

    # Remove large embeddings for this test
    del hyper_test_args['large_embeddings']

    hyper_result = train_ml_model(**hyper_test_args)
    print(f"   Hyperparameter test result: {hyper_result}")

    print("\n✅ All filtering scenarios work perfectly!")


def show_key_benefits():
    """Show the key benefits of the new format."""
    print("\n" + "="*60)
    print("KEY BENEFITS OF NAMED ARGUMENT CAPTURE")
    print("="*60)

    # Load the captured arguments
    args_dict = load_capture_dict("train_ml_model")

    print("\n🎯 PROBLEM SOLVED:")
    print("   - Large ML models, embeddings, datasets are captured")
    print("   - But you don't want them in every test (too slow/memory intensive)")
    print("   - Need to selectively exclude them while maintaining argument order")

    print("\n✅ SOLUTION WITH NAMED ARGS:")
    print("   1. All args captured with parameter names in order")
    print("   2. Easy filtering: {k: v for k, v in args_dict.items() if k != 'large_arg'}")
    print("   3. Replay with order: *args_dict.values()")
    print("   4. Replace specific args: args_dict['param'] = new_value")

    print(f"\n📊 EXAMPLE:")
    print(f"   Original args: {list(args_dict.keys())}")

    # Show filtering in action
    small_args = {k: v for k, v in args_dict.items() if k not in ['data', 'large_embeddings']}
    small_args['data'] = [1, 2, 3]

    print(f"   Filtered args: {list(small_args.keys())}")
    print(f"   Can call: train_ml_model(**filtered_args)")

    print("\n🚀 PERFECT FOR:")
    print("   - ML/AI functions with large weights, embeddings, datasets")
    print("   - Functions with file handles, database connections")
    print("   - Any function where some args are too large for test snapshots")
    print("   - Testing with different argument combinations")


if __name__ == "__main__":
    demonstrate_filtering()
    show_key_benefits()

    print(f"\n{'='*60}")
    print("🎉 The new named argument format solves the large argument problem!")
    print(f"{'='*60}")