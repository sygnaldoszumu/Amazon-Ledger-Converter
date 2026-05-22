"""
get_file_contents module - Simple utility for reading short text files.
"""

from pathlib import Path
from typing import Union, Optional

def get_file_contents(file_path: Union[str, Path]) -> Optional[str]:
    """
    Read and return the contents of a text file.
    
    Args:
        file_path: Path to the file (string or Path object)
    
    Returns:
        File contents as string, or None if file doesn't exist or can't be read
    
    Examples:
        >>> content = get_file_contents('config.txt')
        >>> if content:
        ...     print(content)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            return content
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        print(f"Error reading '{file_path}': {e}")
        return None




# Example usage
if __name__ == "__main__":
    # Read a simple text file
    content = get_file_contents("examples/client_name.txt")
    if content:
        print(content)
