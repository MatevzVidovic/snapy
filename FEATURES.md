# Snapy Features

## Argument Capture System
• Automatic function argument capture via `@capture_args()` decorator
• Pickle-based argument storage with dill fallback
• Configurable capture paths and retention policies
• Argument filtering for sensitive data (passwords, tokens, secrets)
• Production mode with minimal overhead
• Capture replay for test scenarios
• Asynchronous function support
• Context-based capture control

## Function Tracing System
• Real-time function call tracing using `sys.settrace`
• Call event capture (enter, return, exception)
• Execution time measurement
• Call stack depth tracking
• Exception handling and error tracking
• Trace filtering by function patterns
• Performance impact monitoring

## Testing Integration
• Syrupy snapshot testing integration
• TracedSnapshot for function call validation
• Test argument replay from captured data
• Pytest integration with fixtures
• Snapshot comparison for traced execution
• Test data isolation and cleanup

## Configuration Management
• Environment variable configuration
• Global and per-decorator settings
• Runtime configuration updates
• Production vs development modes
• Serialization backend selection (pickle/dill/auto)
• Capture enable/disable controls

## Security Features
• Automatic sensitive argument filtering
• Configurable filter patterns
• Secure storage handling
• Production mode data minimization
• Access control for capture files

## Serialization Support
• Multiple serialization backends (pickle, dill)
• Automatic fallback mechanisms
• Complex object serialization
• Lambda and closure support (via dill)
• Custom object handling

## Error Handling
• Graceful capture failures
• Storage error recovery
• Trace interruption handling
• Configuration validation
• Detailed error reporting