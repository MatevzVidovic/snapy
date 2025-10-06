"""
Simple data structures and functions for showcasing Snapy functionality.

This module demonstrates how Snapy works with various data types that might
be challenging for pickle serialization.
"""

import sys
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from snapy import capture_args

# Try to import optional dependencies
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


# Custom class
class Person:
    def __init__(self, name: str, age: int, skills: List[str]):
        self.name = name
        self.age = age
        self.skills = skills

    def __repr__(self):
        return f"Person(name='{self.name}', age={self.age}, skills={self.skills})"

    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.age == other.age and self.skills == other.skills


# Dataclass
@dataclass
class Product:
    id: int
    name: str
    price: float
    in_stock: bool = True
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


# Simple linked list node
class ListNode:
    def __init__(self, value: Any, next_node: Optional['ListNode'] = None):
        self.value = value
        self.next = next_node

    def __repr__(self):
        return f"ListNode({self.value})"

    def __eq__(self, other):
        if not isinstance(other, ListNode):
            return False
        return self.value == other.value and self.next == other.next


def create_linked_list(values: List[Any]) -> Optional[ListNode]:
    """Helper to create a linked list from a list of values."""
    if not values:
        return None

    head = ListNode(values[0])
    current = head
    for value in values[1:]:
        current.next = ListNode(value)
        current = current.next
    return head


# Functions that work with these data structures

@capture_args(path="./000showcase/captures")
def process_person(person: Person, department: str, salary: float) -> Dict[str, Any]:
    """Process a person's employment data."""
    return {
        "employee": person.name,
        "department": department,
        "salary": salary,
        "skill_count": len(person.skills),
        "is_senior": person.age > 30
    }


@capture_args(path="./000showcase/captures")
def calculate_inventory_value(products: List[Product], discount_rates: Dict[str, float]) -> Dict[str, Any]:
    """Calculate total inventory value with discounts."""
    total_value = 0
    product_count = 0

    for product in products:
        if product.in_stock:
            discount = discount_rates.get(product.name, 0.0)
            discounted_price = product.price * (1 - discount)
            total_value += discounted_price
            product_count += 1

    return {
        "total_value": total_value,
        "product_count": product_count,
        "average_value": total_value / product_count if product_count > 0 else 0
    }


@capture_args(path="./000showcase/captures")
def process_linked_list(head: Optional[ListNode], operation: str) -> Dict[str, Any]:
    """Process a linked list with various operations."""
    if head is None:
        return {"length": 0, "values": [], "operation": operation}

    values = []
    current = head
    while current:
        values.append(current.value)
        current = current.next

    if operation == "sum" and all(isinstance(v, (int, float)) for v in values):
        result = sum(values)
    elif operation == "concat" and all(isinstance(v, str) for v in values):
        result = "".join(values)
    else:
        result = values

    return {
        "length": len(values),
        "values": values,
        "operation": operation,
        "result": result
    }


# Numpy functions (if available)
if HAS_NUMPY:
    @capture_args(path="./000showcase/captures")
    def analyze_numpy_array(data: np.ndarray, weights: np.ndarray) -> Dict[str, Any]:
        """Analyze numpy array data with weights."""
        return {
            "shape": data.shape,
            "mean": float(np.mean(data)),
            "weighted_mean": float(np.average(data, weights=weights)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data))
        }


# Pandas functions (if available)
if HAS_PANDAS:
    @capture_args(path="./000showcase/captures")
    def process_dataframe(df: pd.DataFrame, group_by: str, agg_column: str) -> Dict[str, Any]:
        """Process pandas DataFrame with grouping and aggregation."""
        grouped = df.groupby(group_by)[agg_column].agg(['mean', 'sum', 'count'])

        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "group_by": group_by,
            "agg_column": agg_column,
            "grouped_stats": grouped.to_dict()
        }


@capture_args(path="./000showcase/captures")
def complex_nested_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a complex nested dictionary structure."""
    def count_nested_items(obj, depth=0):
        if isinstance(obj, dict):
            return sum(count_nested_items(v, depth + 1) for v in obj.values())
        elif isinstance(obj, (list, tuple)):
            return sum(count_nested_items(item, depth + 1) for item in obj)
        else:
            return 1

    return {
        "total_items": count_nested_items(data),
        "top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
        "structure_type": type(data).__name__,
        "serializable": True  # We'll see if this stays true after pickle!
    }


def main():
    """Demonstrate all the functions with various data structures."""
    print("🎯 Snapy Showcase - Testing Complex Data Structures")
    print("=" * 50)

    # Test Person class
    person = Person("Alice Smith", 35, ["Python", "Data Science", "Machine Learning"])
    result1 = process_person(person, "Engineering", 95000.0)
    print(f"✅ Processed person: {result1}")

    # Test Product dataclass
    products = [
        Product(1, "laptop", 999.99, True, ["electronics", "computers"]),
        Product(2, "mouse", 29.99, True, ["electronics", "accessories"]),
        Product(3, "keyboard", 79.99, False, ["electronics", "accessories"])
    ]
    discounts = {"laptop": 0.1, "mouse": 0.05}
    result2 = calculate_inventory_value(products, discounts)
    print(f"✅ Calculated inventory: {result2}")

    # Test linked list
    linked_list = create_linked_list([1, 2, 3, 4, 5])
    result3 = process_linked_list(linked_list, "sum")
    print(f"✅ Processed linked list: {result3}")

    # Test complex nested structure
    complex_data = {
        "users": [
            {"id": 1, "name": "Alice", "preferences": {"theme": "dark", "notifications": True}},
            {"id": 2, "name": "Bob", "preferences": {"theme": "light", "notifications": False}}
        ],
        "settings": {
            "app_version": "2.0.0",
            "features": ["capture", "testing", "tracing"],
            "limits": {"max_users": 1000, "max_captures": 500}
        }
    }
    result4 = complex_nested_structure(complex_data)
    print(f"✅ Processed complex structure: {result4}")

    # Test numpy (if available)
    if HAS_NUMPY:
        data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
        weights = np.array([0.3, 0.5, 0.2])
        result5 = analyze_numpy_array(data.flatten(), weights)
        print(f"✅ Analyzed numpy array: {result5}")
    else:
        print("⚠️  Numpy not available - skipping numpy tests")

    # Test pandas (if available)
    if HAS_PANDAS:
        df_data = {
            'category': ['A', 'B', 'A', 'B', 'A', 'C'],
            'value': [10, 20, 15, 25, 12, 30],
            'count': [1, 2, 1, 3, 2, 1]
        }
        df = pd.DataFrame(df_data)
        result6 = process_dataframe(df, 'category', 'value')
        print(f"✅ Processed pandas DataFrame: {result6}")
    else:
        print("⚠️  Pandas not available - skipping pandas tests")

    print("\n🎉 All functions executed! Check ./000showcase/captures/ for captured arguments.")


if __name__ == "__main__":
    main()