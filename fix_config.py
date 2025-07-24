# Fix the formatting of the config file
import re

with open('clickup/core/config.py', 'r') as f:
    content = f.read()

# Fix the method definitions that have embedded newlines
content = re.sub(r'def set_default_list\(self, alias: str, list_id: str\) -> None:\\n        """Set a default list with an alias."""\\n        self\._config\.default_lists\[alias\] = list_id\\n        self\.save_config\(\)\\n\\n    def get_default_list\(self, alias: str\) -> str \| None:\\n        """Get a default list ID by alias."""\\n        return self\._config\.default_lists\.get\(alias\)\\n\\n    def get_default_lists\(self\) -> dict\[str, str\]:\\n        """Get all default lists."""\\n        return self\._config\.default_lists\.copy\(\)\\n\\n    def remove_default_list\(self, alias: str\) -> bool:\\n        """Remove a default list alias\. Returns True if removed, False if not found\."""\\n        if alias in self\._config\.default_lists:\\n            del self\._config\.default_lists\[alias\]\\n            self\.save_config\(\)\\n            return True\\n        return False\\n\\n    def resolve_list_id\(self, list_ref: str\) -> str:\\n        """Resolve a list reference \(ID or alias\) to a list ID\.\\n        \\n        Args:\\n            list_ref: Either a list ID or an alias\\n            \\n        Returns:\\n            The resolved list ID\\n            \\n        Raises:\\n            ValueError: If the alias is not found\\n        """\\n        # If it\'s already a list ID \(numeric\), return as-is\\n        if list_ref\.isdigit\(\):\\n            return list_ref\\n            \\n        # Try to resolve as alias\\n        list_id = self\.get_default_list\(list_ref\)\\n        if list_id:\\n            return list_id\\n            \\n        # If not found, raise error with helpful message\\n        available_aliases = list\(self\._config\.default_lists\.keys\(\)\)\\n        if available_aliases:\\n            aliases_str = ", "\.join\(available_aliases\)\\n            raise ValueError\(f"Unknown list alias \'{list_ref}\'". Available aliases: {aliases_str}"\)\\n        else:\\n            raise ValueError\(f"Unknown list alias \'{list_ref}\'". No default lists configured\. Use \'clickup config set-default-list\' to configure aliases\."\)\\n\\n    def get_headers', '''
    def set_default_list(self, alias: str, list_id: str) -> None:
        """Set a default list with an alias."""
        self._config.default_lists[alias] = list_id
        self.save_config()

    def get_default_list(self, alias: str) -> str | None:
        """Get a default list ID by alias."""
        return self._config.default_lists.get(alias)

    def get_default_lists(self) -> dict[str, str]:
        """Get all default lists."""
        return self._config.default_lists.copy()

    def remove_default_list(self, alias: str) -> bool:
        """Remove a default list alias. Returns True if removed, False if not found."""
        if alias in self._config.default_lists:
            del self._config.default_lists[alias]
            self.save_config()
            return True
        return False

    def resolve_list_id(self, list_ref: str) -> str:
        """Resolve a list reference (ID or alias) to a list ID.
        
        Args:
            list_ref: Either a list ID or an alias
            
        Returns:
            The resolved list ID
            
        Raises:
            ValueError: If the alias is not found
        """
        # If it's already a list ID (numeric), return as-is
        if list_ref.isdigit():
            return list_ref
            
        # Try to resolve as alias
        list_id = self.get_default_list(list_ref)
        if list_id:
            return list_id
            
        # If not found, raise error with helpful message
        available_aliases = list(self._config.default_lists.keys())
        if available_aliases:
            aliases_str = ", ".join(available_aliases)
            raise ValueError(f"Unknown list alias '{list_ref}'. Available aliases: {aliases_str}")
        else:
            raise ValueError(f"Unknown list alias '{list_ref}'. No default lists configured. Use 'clickup config set-default-list' to configure aliases.")

    def get_headers''')

with open('clickup/core/config.py', 'w') as f:
    f.write(content)
