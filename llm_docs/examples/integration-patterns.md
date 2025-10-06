# PySnap Integration Patterns and Examples

## Complete Integration Examples

### 1. E-commerce Order Processing

This example demonstrates comprehensive testing of a complex business workflow using both snapy_capture and snapy_testing.

```python
# src/ecommerce/order_service.py
from snapy_capture import capture_args
from decimal import Decimal

class OrderService:
    def __init__(self, payment_service, inventory_service, notification_service):
        self.payment_service = payment_service
        self.inventory_service = inventory_service
        self.notification_service = notification_service

    @capture_args(
        path="./order_captures",
        retention=5,
        ignore_args=["payment_token", "customer_secret"]
    )
    def process_order(self, customer_id, items, payment_token, shipping_address):
        """Complete order processing workflow"""
        # Validate inventory
        availability = self.inventory_service.check_availability(items)
        if not availability['available']:
            raise OrderError(f"Items not available: {availability['missing']}")

        # Calculate pricing
        pricing = self._calculate_pricing(items, shipping_address)
        total_amount = pricing['total']

        # Process payment
        payment_result = self.payment_service.charge_payment(
            payment_token,
            total_amount,
            customer_id
        )

        if not payment_result['success']:
            raise PaymentError(payment_result['error'])

        # Reserve inventory
        reservation_id = self.inventory_service.reserve_items(
            items,
            customer_id,
            expires_in=3600
        )

        # Create order record
        order = self._create_order_record(
            customer_id,
            items,
            pricing,
            payment_result['transaction_id'],
            reservation_id
        )

        # Send confirmation
        self.notification_service.send_order_confirmation(
            customer_id,
            order['order_id']
        )

        return {
            'order_id': order['order_id'],
            'total_amount': total_amount,
            'estimated_delivery': order['estimated_delivery']
        }

    def _calculate_pricing(self, items, shipping_address):
        # Complex pricing logic with taxes, discounts, shipping
        pass

    def _create_order_record(self, customer_id, items, pricing, transaction_id, reservation_id):
        # Database order creation
        pass
```

**Testing with Captured Arguments**:
```python
# tests/test_order_service.py
import pytest
from snapy_capture import load_capture, has_capture
from snapy_testing import TracedSnapshot
from unittest.mock import Mock

class TestOrderService:

    def test_order_processing_with_captured_data(self, snapshot):
        """Test order processing using real captured arguments"""

        # Load real arguments from production-like scenario
        if has_capture("process_order"):
            args, kwargs = load_capture("process_order")
        else:
            # Fallback to manual test data
            args, kwargs = self._get_test_order_data()

        # Mock external services with realistic responses
        payment_service = Mock()
        payment_service.charge_payment.return_value = {
            'success': True,
            'transaction_id': 'txn_12345'
        }

        inventory_service = Mock()
        inventory_service.check_availability.return_value = {
            'available': True,
            'missing': []
        }
        inventory_service.reserve_items.return_value = 'reservation_789'

        notification_service = Mock()

        # Create service with mocks
        order_service = OrderService(
            payment_service,
            inventory_service,
            notification_service
        )

        # Execute with tracing to capture full workflow
        traced = TracedSnapshot(detail_level="verbose")
        with traced:
            result = order_service.process_order(*args, **kwargs)

        # Comprehensive snapshot including result and execution trace
        complete_test_data = {
            'order_result': result,
            'execution_trace': traced.format_trace(),
            'service_interactions': {
                'payment_calls': payment_service.charge_payment.call_args_list,
                'inventory_calls': {
                    'availability_checks': inventory_service.check_availability.call_args_list,
                    'reservations': inventory_service.reserve_items.call_args_list
                },
                'notification_calls': notification_service.send_order_confirmation.call_args_list
            },
            'performance_metrics': traced.get_performance_metrics()
        }

        assert complete_test_data == snapshot

    def test_order_error_scenarios(self, snapshot):
        """Test error handling with traced execution"""

        # Test inventory unavailable scenario
        traced = TracedSnapshot()

        with traced:
            with pytest.raises(OrderError):
                # Use captured args that should trigger inventory error
                args, kwargs = load_capture("process_order", index=1)  # Different scenario
                result = order_service.process_order(*args, **kwargs)

        error_trace = {
            'error_type': 'OrderError',
            'execution_flow': traced.format_trace(),
            'failed_at_step': self._identify_failure_point(traced.get_events()),
            'service_state': self._capture_service_state_at_failure()
        }

        assert error_trace == snapshot
```

### 2. Data Processing Pipeline

Example of testing a complex data transformation pipeline with multiple stages.

```python
# src/data/pipeline.py
from snapy_capture import capture_args
from snapy_testing import FunctionTracer
import pandas as pd

class DataPipeline:

    @capture_args(
        path="./pipeline_captures",
        ignore_args=["credentials"],
        retention=3
    )
    def process_customer_data(self, raw_data_path, credentials, output_format="json"):
        """Multi-stage data processing pipeline"""

        # Stage 1: Data ingestion
        raw_data = self._ingest_data(raw_data_path, credentials)

        # Stage 2: Data validation and cleaning
        validated_data = self._validate_and_clean(raw_data)

        # Stage 3: Data enrichment
        enriched_data = self._enrich_data(validated_data)

        # Stage 4: Data aggregation
        aggregated_data = self._aggregate_data(enriched_data)

        # Stage 5: Output formatting
        formatted_output = self._format_output(aggregated_data, output_format)

        return {
            'processed_records': len(formatted_output),
            'data': formatted_output,
            'pipeline_stats': self._get_pipeline_stats()
        }

    def _ingest_data(self, path, credentials):
        # Data ingestion logic
        pass

    def _validate_and_clean(self, data):
        # Data validation and cleaning
        pass

    def _enrich_data(self, data):
        # Data enrichment with external sources
        pass

    def _aggregate_data(self, data):
        # Data aggregation and summarization
        pass

    def _format_output(self, data, format_type):
        # Output formatting
        pass
```

**Comprehensive Pipeline Testing**:
```python
# tests/test_data_pipeline.py
def test_complete_pipeline_with_tracing(snapshot):
    """Test entire pipeline with detailed execution tracing"""

    # Load captured real-world arguments
    args, kwargs = load_capture("process_customer_data")

    # Create tracer with pipeline-specific filtering
    tracer = FunctionTracer(filter_modules=[
        "data.*",          # Our data processing modules
        "pandas.*",        # Pandas operations
        "!numpy.*"         # Exclude numpy internals
    ])

    pipeline = DataPipeline()

    with tracer:
        result = pipeline.process_customer_data(*args, **kwargs)

    # Comprehensive analysis of pipeline execution
    pipeline_analysis = {
        'result_summary': {
            'records_processed': result['processed_records'],
            'output_format': kwargs.get('output_format', 'json')
        },
        'execution_analysis': {
            'total_execution_time': tracer.get_metrics()['total_time'],
            'stage_breakdown': _analyze_pipeline_stages(tracer.get_events()),
            'performance_bottlenecks': _identify_bottlenecks(tracer.get_events()),
            'function_call_graph': tracer.get_call_graph()
        },
        'data_quality_metrics': result['pipeline_stats'],
        'resource_usage': tracer.get_metrics()['memory_usage']
    }

    assert pipeline_analysis == snapshot

def _analyze_pipeline_stages(events):
    """Analyze execution time per pipeline stage"""
    stage_methods = [
        '_ingest_data', '_validate_and_clean', '_enrich_data',
        '_aggregate_data', '_format_output'
    ]

    stage_analysis = {}
    for method in stage_methods:
        method_events = [e for e in events if e.function_name == method]
        if method_events:
            call_event = method_events[0]
            return_event = method_events[1] if len(method_events) > 1 else None

            stage_analysis[method] = {
                'execution_time': return_event.duration if return_event else None,
                'arguments_size': len(str(call_event.args)),
                'memory_at_start': call_event.memory_usage
            }

    return stage_analysis
```

### 3. Machine Learning Model Training

Example of capturing and testing ML model training workflows.

```python
# src/ml/model_trainer.py
from snapy_capture import capture_args
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class ModelTrainer:

    @capture_args(
        path="./ml_captures",
        retention=2,
        ignore_args=["api_credentials"],  # Don't capture external API credentials
        # Large datasets might need special handling
        custom_filters=[lambda name, value: name != 'training_data' or len(value) < 10000]
    )
    def train_model(self, training_data, target_variable, api_credentials=None, hyperparameters=None):
        """Train ML model with comprehensive tracking"""

        # Data preprocessing
        X_processed, y_processed = self._preprocess_data(training_data, target_variable)

        # Feature engineering
        X_features = self._engineer_features(X_processed)

        # Model training
        model = self._train_with_hyperparameters(X_features, y_processed, hyperparameters)

        # Model evaluation
        evaluation_metrics = self._evaluate_model(model, X_features, y_processed)

        # Model persistence
        model_path = self._save_model(model, evaluation_metrics)

        return {
            'model_path': model_path,
            'evaluation_metrics': evaluation_metrics,
            'feature_importance': model.feature_importances_.tolist(),
            'training_summary': {
                'samples_trained': len(X_features),
                'features_used': X_features.shape[1],
                'model_type': type(model).__name__
            }
        }
```

**ML Training Test with Execution Tracing**:
```python
# tests/test_model_trainer.py
def test_model_training_workflow(snapshot):
    """Test ML training with captured data and execution tracing"""

    # Load captured training arguments (with large data handling)
    args, kwargs = load_capture("train_model")

    # Create tracer focused on ML workflow
    tracer = FunctionTracer(filter_modules=[
        "ml.*",           # Our ML modules
        "sklearn.*",      # Scikit-learn operations
        "!numpy.*",       # Exclude numpy internals for performance
        "!pandas.*"       # Exclude pandas internals
    ])

    trainer = ModelTrainer()

    with tracer:
        result = trainer.train_model(*args, **kwargs)

    # Comprehensive ML workflow analysis
    ml_analysis = {
        'training_results': {
            'model_performance': result['evaluation_metrics'],
            'feature_count': result['training_summary']['features_used'],
            'samples_processed': result['training_summary']['samples_trained']
        },
        'workflow_analysis': {
            'execution_flow': tracer.format_trace(format_type="tree"),
            'performance_metrics': tracer.get_metrics(),
            'ml_operations': _extract_ml_operations(tracer.get_events()),
            'data_transformation_steps': _analyze_data_transformations(tracer.get_events())
        },
        'model_quality': {
            'feature_importance': result['feature_importance'][:10],  # Top 10 features
            'training_stability': _assess_training_stability(tracer.get_events())
        }
    }

    assert ml_analysis == snapshot

def _extract_ml_operations(events):
    """Extract ML-specific operations from trace"""
    ml_operations = []
    sklearn_events = [e for e in events if 'sklearn' in e.module_name]

    for event in sklearn_events:
        if event.is_call_event():
            ml_operations.append({
                'operation': event.function_name,
                'module': event.module_name,
                'execution_time': getattr(event, 'duration', None),
                'parameters': _sanitize_ml_parameters(event.args)
            })

    return ml_operations
```

## Integration Best Practices

### 1. Security-First Capture Configuration

```python
# config/capture_security.py
from snapy_capture import CaptureConfig, ArgumentFilter
import re

class ProductionSecureFilter(ArgumentFilter):
    """Production-ready security filter"""

    def __init__(self):
        super().__init__()
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',        # SSN
            r'\b\d{16}\b',                    # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{10}\b',                    # Phone number
        ]
        self.sensitive_keys = [
            'password', 'token', 'secret', 'key', 'credential',
            'api_key', 'access_token', 'session_id', 'oauth_token'
        ]

    def should_capture_arg(self, arg_name, arg_value):
        # Check sensitive argument names
        if any(sensitive in arg_name.lower() for sensitive in self.sensitive_keys):
            return False

        # Check for PII patterns in string values
        if isinstance(arg_value, str):
            for pattern in self.pii_patterns:
                if re.search(pattern, arg_value):
                    return False

        return super().should_capture_arg(arg_name, arg_value)

# Production configuration
production_config = CaptureConfig(
    production_mode=True,
    minimal_capture=True,
    default_retention=1,
    ignore_args=['password', 'token', 'secret', 'credentials', 'api_key'],
    custom_filter=ProductionSecureFilter()
)
```

### 2. Performance-Optimized Tracing

```python
# config/performance_config.py
from snapy_testing import FunctionTracer, TracerConfig

class HighPerformanceTracer(FunctionTracer):
    """Optimized tracer for production-like environments"""

    def __init__(self, sampling_rate=0.1):
        config = TracerConfig(
            max_events=5000,           # Limit memory usage
            enable_line_tracing=False, # Disable line-by-line for performance
            capture_locals=False,      # Don't capture local variables
            memory_tracking=False,     # Disable memory tracking
            compression=True,          # Enable event compression
            auto_cleanup=True          # Automatic cleanup
        )

        super().__init__(
            filter_modules=["myapp.*", "!third_party.*"],
            config=config
        )

        self.sampling_rate = sampling_rate

    def should_trace_call(self, frame, event, arg):
        # Implement sampling for high-frequency scenarios
        if random.random() > self.sampling_rate:
            return False

        return super().should_trace_call(frame, event, arg)
```

### 3. Test Data Management

```python
# tests/conftest.py
import pytest
from snapy_capture import load_capture, has_capture, CaptureLoader

@pytest.fixture
def captured_data():
    """Intelligent capture loading with fallbacks"""

    def _load_capture_with_fallback(function_name, fallback_data=None):
        if has_capture(function_name):
            return load_capture(function_name)
        elif fallback_data:
            return fallback_data
        else:
            pytest.skip(f"No captured data available for {function_name}")

    return _load_capture_with_fallback

@pytest.fixture
def capture_loader():
    """Advanced capture loading with filtering"""
    return CaptureLoader()

# Usage in tests
def test_with_intelligent_loading(captured_data, snapshot):
    args, kwargs = captured_data(
        "complex_function",
        fallback_data=get_default_test_data()
    )

    result = complex_function(*args, **kwargs)
    assert result == snapshot
```

This comprehensive integration guide demonstrates how to effectively combine snapy_capture and snapy_testing for real-world testing scenarios while maintaining security, performance, and maintainability.