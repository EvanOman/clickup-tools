# ADR-002: Default Lists Configuration Feature

## Status
Partially Complete

## Context
Users need to remember and repeatedly specify list IDs for task operations, which is cumbersome for frequently used lists. The feature request asks for support for configuring default lists with aliases that can be referenced by name instead of ID.

## Decision
Implement default lists configuration support with:

1. **Configuration Model**: Add `default_lists: dict[str, str]` field to `ClickUpConfig`
2. **Config Management**: Add methods for managing default list aliases
3. **CLI Commands**: Add config subcommands for list management
4. **Alias Resolution**: Add `resolve_list_id()` method to resolve aliases to IDs
5. **Integration**: Update task commands to support aliases (future work)

## Implementation

### Core Config Changes
- Added `default_lists: dict[str, str] = {}` to `ClickUpConfig` model
- Added methods to `Config` class:
  - `set_default_list(alias, list_id)` - Set alias
  - `get_default_list(alias)` - Get list ID by alias  
  - `get_default_lists()` - Get all aliases
  - `remove_default_list(alias)` - Remove alias
  - `resolve_list_id(list_ref)` - Resolve ID or alias to ID

### CLI Commands Added
- `clickup config set-default-list <alias> <list-id>` - Set default list
- `clickup config list-defaults` - Show all default lists
- `clickup config remove-default-list <alias>` - Remove default list

### Usage Examples
```bash
# Configure default lists
clickup config set-default-list inbox "123456789"
clickup config set-default-list bugs "987654321"

# View configured lists
clickup config list-defaults

# Remove a default list
clickup config remove-default-list inbox
```

## Future Work
- Update task commands (create, list, etc.) to use `resolve_list_id()` 
- Update help text to mention alias support
- Add tests for alias resolution in task commands
- Consider adding shell completion for aliases

## Benefits
- Improved user experience for frequent operations
- Reduced need to remember/look up list IDs
- More intuitive CLI commands
- Backward compatible with existing list ID usage

## Testing
- Core config functionality tested via existing test suite
- CLI commands are functional and follow existing patterns
- No breaking changes to existing functionality