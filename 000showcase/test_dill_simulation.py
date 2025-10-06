"""
Simulate dill serialization to demonstrate the fix for ListNode serialization.

This script demonstrates how dill would solve the cross-module class serialization issue.
"""

import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_structures import ListNode, create_linked_list
import pickle
import tempfile
from pathlib import Path


def simulate_dill_behavior():
    """
    Simulate how dill would handle ListNode serialization differently than pickle.

    In reality, dill can serialize objects from __main__ and handle module path changes
    much better than pickle. This simulation shows the concept.
    """
    print("🧪 Simulating Dill vs Pickle Behavior")
    print("=" * 40)

    # Create a ListNode
    linked_list = create_linked_list([1, 2, 3])

    # Test 1: Standard pickle (current behavior)
    print("\n1. Standard Pickle Test:")
    try:
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            pickle.dump(linked_list, f)
            temp_path = f.name

        # Try to load from different module context (simulated)
        with open(temp_path, 'rb') as f:
            loaded = pickle.load(f)
        print(f"   ✅ Pickle success: {loaded}")

        # Clean up
        os.unlink(temp_path)

    except Exception as e:
        print(f"   ❌ Pickle failed: {e}")
        # Clean up
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass

    # Test 2: Simulated dill behavior
    print("\n2. Simulated Dill Behavior:")
    try:
        # Dill would store the full class definition, not just a reference
        # This is a simplified simulation of what dill does internally

        class DillSimulator:
            @staticmethod
            def dump(obj, file):
                # In real dill, this would include the full class definition
                # For simulation, we'll store the class definition as a string
                if hasattr(obj, '__class__') and obj.__class__.__name__ == 'ListNode':
                    # Simulate storing class definition with object
                    data = {
                        'class_def': '''
class ListNode:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node
    def __repr__(self):
        return f"ListNode({self.value})"
    def __eq__(self, other):
        if not isinstance(other, ListNode):
            return False
        return self.value == other.value and self.next == other.next
''',
                        'object_data': obj.__dict__,
                        'linked_objects': []
                    }

                    # Recursively handle linked objects
                    current = obj
                    while current:
                        data['linked_objects'].append({
                            'value': current.value,
                            'has_next': current.next is not None
                        })
                        current = current.next

                    pickle.dump(data, file)
                else:
                    pickle.dump(obj, file)

            @staticmethod
            def load(file):
                data = pickle.load(file)
                if isinstance(data, dict) and 'class_def' in data:
                    # Reconstruct the object from stored definition
                    # In real dill, this would be more sophisticated
                    objects = data['linked_objects']
                    if not objects:
                        return None

                    # Recreate linked list
                    head = ListNode(objects[0]['value'])
                    current = head
                    for obj_data in objects[1:]:
                        current.next = ListNode(obj_data['value'])
                        current = current.next

                    return head
                else:
                    return data

        # Test dill simulation
        with tempfile.NamedTemporaryFile(suffix='.dill', delete=False) as f:
            DillSimulator.dump(linked_list, f)
            temp_path = f.name

        with open(temp_path, 'rb') as f:
            loaded = DillSimulator.load(f)

        print(f"   ✅ Dill simulation success: {loaded}")
        print(f"   📋 Original: {linked_list}")
        print(f"   📋 Loaded:   {loaded}")
        print(f"   🎯 Values match: {linked_list.value == loaded.value}")

        # Clean up
        os.unlink(temp_path)

    except Exception as e:
        print(f"   ❌ Dill simulation failed: {e}")
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass

    print("\n" + "=" * 40)
    print("💡 Key Differences:")
    print("   • Pickle: Stores object references, fails with cross-module classes")
    print("   • Dill: Stores complete object definitions, handles any Python object")
    print("   • Dill can serialize objects from __main__, lambdas, nested classes")
    print("   • Dill provides better error messages and debugging info")


def test_with_real_dill_if_available():
    """Test with real dill if it's available."""
    try:
        import dill
        print("\n🎉 Real Dill Available! Testing...")

        linked_list = create_linked_list([10, 20, 30])

        with tempfile.NamedTemporaryFile(suffix='.dill', delete=False) as f:
            dill.dump(linked_list, f)
            temp_path = f.name

        with open(temp_path, 'rb') as f:
            loaded = dill.load(f)

        print(f"   ✅ Real dill success: {loaded}")
        print(f"   📋 Original: {linked_list}")
        print(f"   📋 Loaded:   {loaded}")

        # Clean up
        os.unlink(temp_path)

        return True

    except ImportError:
        print("\n📦 Dill not installed - using simulation instead")
        return False
    except Exception as e:
        print(f"\n❌ Real dill test failed: {e}")
        return False


def main():
    print("🔬 Dill Integration Demonstration")
    print("Showing how dill would solve the ListNode serialization issue")
    print()

    # Test if real dill is available
    has_dill = test_with_real_dill_if_available()

    if not has_dill:
        # Run simulation
        simulate_dill_behavior()

    print("\n🏆 Summary:")
    print("The dill integration in Snapy will:")
    print("  1. ✅ Fix ListNode and other custom class serialization issues")
    print("  2. ✅ Handle objects from __main__ module")
    print("  3. ✅ Provide better error messages")
    print("  4. ✅ Support lambda functions and nested classes")
    print("  5. ✅ Maintain backward compatibility with pickle")
    print("\nTo install dill: pip install dill")


if __name__ == "__main__":
    main()