import inspect
import sys
from collections import defaultdict
from typing import Any

class BuiltinTypeInspector:
    def __init__(self):
        """Initialize the built-in type inspector."""
        self.builtin_types = {
            'str': str,
            'int': int,
            'float': float,
            'complex': complex,
            'list': list,
            'tuple': tuple,
            'dict': dict,
            'set': set,
            'frozenset': frozenset,
            'bool': bool,
            'bytes': bytes,
            'bytearray': bytearray,
            'memoryview': memoryview,
            'range': range,
            'slice': slice,
            'type': type,
            'object': object,
        }
        self.current_type = None
        self.current_type_name = None
    
    def list_available_types(self):
        """List all available built-in types."""
        print("\n" + "=" * 100)
        print("🐍 AVAILABLE BUILT-IN TYPES")
        print("=" * 100)
        
        categories = {
            'Numeric Types': ['int', 'float', 'complex', 'bool'],
            'Sequence Types': ['str', 'list', 'tuple', 'range'],
            'Set Types': ['set', 'frozenset'],
            'Mapping Types': ['dict'],
            'Binary Types': ['bytes', 'bytearray', 'memoryview'],
            'Other Types': ['slice', 'type', 'object']
        }
        
        for category, types in categories.items():
            print(f"\n📦 {category}:")
            for i, type_name in enumerate(types, 1):
                print(f"  [{i}] {type_name}")
    
    def load_type(self, type_name):
        """Load a built-in type for inspection."""
        if type_name in self.builtin_types:
            self.current_type = self.builtin_types[type_name]
            self.current_type_name = type_name
            print(f"✅ Successfully loaded type '{type_name}'")
            return True
        else:
            print(f"❌ Error: '{type_name}' is not a recognized built-in type")
            print(f"   Available types: {', '.join(sorted(self.builtin_types.keys()))}")
            return False
    
    def categorize_methods(self, type_obj):
        """Categorize methods into different groups."""
        categories = {
            'constructors': [],
            'magic_methods': [],
            'query_methods': [],
            'mutation_methods': [],
            'conversion_methods': [],
            'operators': [],
            'other_methods': []
        }
        
        for name in dir(type_obj):
            if not callable(getattr(type_obj, name, None)):
                continue
            
            # Skip private methods (except magic methods)
            if name.startswith('_') and not (name.startswith('__') and name.endswith('__')):
                continue
            
            # Magic methods (dunder methods)
            if name.startswith('__') and name.endswith('__'):
                if name in ['__new__', '__init__', '__init_subclass__']:
                    categories['constructors'].append(name)
                elif name.startswith('__r') and name.endswith('__'):  # Reverse operators
                    categories['operators'].append(name)
                elif name in ['__add__', '__sub__', '__mul__', '__truediv__', '__floordiv__', 
                             '__mod__', '__pow__', '__and__', '__or__', '__xor__', '__lshift__', 
                             '__rshift__', '__lt__', '__le__', '__gt__', '__ge__', '__eq__', '__ne__']:
                    categories['operators'].append(name)
                else:
                    categories['magic_methods'].append(name)
            else:
                # Regular methods
                method_lower = name.lower()
                
                # Check if it's a conversion method
                if name.startswith('to') or name in ['hex', 'bin', 'oct', 'encode', 'decode']:
                    categories['conversion_methods'].append(name)
                # Check if it's a query method (doesn't modify)
                elif any(prefix in method_lower for prefix in ['is', 'has', 'get', 'find', 'index', 'count', 'starts', 'ends']):
                    categories['query_methods'].append(name)
                # Check if it's likely a mutation method
                elif any(word in method_lower for word in ['add', 'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'update', 'set', 'del', 'replace', 'sort', 'reverse']):
                    categories['mutation_methods'].append(name)
                else:
                    categories['other_methods'].append(name)
        
        return categories
    
    def get_method_signature(self, type_obj, method_name):
        """Get the signature of a method."""
        try:
            method = getattr(type_obj, method_name)
            sig = inspect.signature(method)
            return str(sig)
        except:
            return "(...)"
    
    def get_method_doc(self, type_obj, method_name):
        """Get the docstring of a method."""
        try:
            method = getattr(type_obj, method_name)
            doc = inspect.getdoc(method)
            if doc:
                # Get first line only
                first_line = doc.split('\n')[0].strip()
                return first_line[:80] + ('...' if len(first_line) > 80 else '')
            return None
        except:
            return None
    
    def analyze_type(self):
        """Analyze the current built-in type."""
        if not self.current_type:
            print("⚠️  No type loaded. Please load a type first.")
            return
        
        print("\n" + "=" * 100)
        print(f"🔍 ANALYZING TYPE: {self.current_type_name}")
        print("=" * 100)
        
        # Basic information
        print(f"\n📍 TYPE INFORMATION")
        print("-" * 100)
        print(f"  Name: {self.current_type_name}")
        print(f"  Type: {type(self.current_type)}")
        print(f"  Module: {self.current_type.__module__}")
        
        # MRO (Method Resolution Order)
        mro = self.current_type.__mro__
        if len(mro) > 1:
            print(f"  Inheritance chain:")
            for base in mro:
                print(f"    └─ {base.__name__}")
        
        # Documentation
        if self.current_type.__doc__:
            doc = self.current_type.__doc__.strip().split('\n')[0]
            print(f"\n  Description:")
            print(f"    {doc}")
        
        # Categorize methods
        categories = self.categorize_methods(self.current_type)
        
        # Print constructors
        if categories['constructors']:
            print(f"\n🏗️  CONSTRUCTORS & INITIALIZATION ({len(categories['constructors'])})")
            print("-" * 100)
            for i, method_name in enumerate(sorted(categories['constructors']), 1):
                sig = self.get_method_signature(self.current_type, method_name)
                print(f"  [{i}] {method_name}{sig}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
        
        # Print query methods
        if categories['query_methods']:
            print(f"\n🔍 QUERY METHODS (don't modify the object) ({len(categories['query_methods'])})")
            print("-" * 100)
            for i, method_name in enumerate(sorted(categories['query_methods']), 1):
                sig = self.get_method_signature(self.current_type, method_name)
                print(f"  [{i}] {method_name}{sig}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
        
        # Print mutation methods
        if categories['mutation_methods']:
            print(f"\n🔧 MUTATION METHODS (modify the object) ({len(categories['mutation_methods'])})")
            print("-" * 100)
            for i, method_name in enumerate(sorted(categories['mutation_methods']), 1):
                sig = self.get_method_signature(self.current_type, method_name)
                print(f"  [{i}] {method_name}{sig}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
        
        # Print conversion methods
        if categories['conversion_methods']:
            print(f"\n🔄 CONVERSION METHODS ({len(categories['conversion_methods'])})")
            print("-" * 100)
            for i, method_name in enumerate(sorted(categories['conversion_methods']), 1):
                sig = self.get_method_signature(self.current_type, method_name)
                print(f"  [{i}] {method_name}{sig}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
        
        # Print operators
        if categories['operators']:
            print(f"\n⚡ OPERATOR OVERLOADS ({len(categories['operators'])})")
            print("-" * 100)
            
            operator_map = {
                '__add__': '+', '__sub__': '-', '__mul__': '*', '__truediv__': '/',
                '__floordiv__': '//', '__mod__': '%', '__pow__': '**',
                '__and__': '&', '__or__': '|', '__xor__': '^',
                '__lshift__': '<<', '__rshift__': '>>',
                '__lt__': '<', '__le__': '<=', '__gt__': '>', '__ge__': '>=',
                '__eq__': '==', '__ne__': '!='
            }
            
            for i, method_name in enumerate(sorted(categories['operators']), 1):
                operator = operator_map.get(method_name, '')
                if operator:
                    print(f"  [{i}] {method_name} → {operator}")
                else:
                    print(f"  [{i}] {method_name}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
        
        # Print magic methods
        if categories['magic_methods']:
            print(f"\n✨ SPECIAL METHODS (magic methods) ({len(categories['magic_methods'])})")
            print("-" * 100)
            for i, method_name in enumerate(sorted(categories['magic_methods']), 1):
                sig = self.get_method_signature(self.current_type, method_name)
                print(f"  [{i}] {method_name}{sig}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
        
        # Print other methods
        if categories['other_methods']:
            print(f"\n📚 OTHER METHODS ({len(categories['other_methods'])})")
            print("-" * 100)
            for i, method_name in enumerate(sorted(categories['other_methods']), 1):
                sig = self.get_method_signature(self.current_type, method_name)
                print(f"  [{i}] {method_name}{sig}")
                doc = self.get_method_doc(self.current_type, method_name)
                if doc:
                    print(f"      ↳ {doc}")
    
    def show_examples(self):
        """Show practical examples for the current type."""
        if not self.current_type:
            print("⚠️  No type loaded. Please load a type first.")
            return
        
        examples = {
            'str': """
🎯 PRACTICAL EXAMPLES FOR str

# Creation
s = "hello world"
s = 'single quotes'
s = '''multiline
string'''

# Common operations
s.upper()              # "HELLO WORLD"
s.capitalize()         # "Hello world"
s.split()              # ["hello", "world"]
s.replace("world", "python")  # "hello python"
s.find("world")        # 6
s.startswith("hello")  # True
len(s)                 # 11

# Formatting
name = "Alice"
f"Hello {name}"        # "Hello Alice"
"Hello {}".format(name)  # "Hello Alice"

# Useful methods
s.strip()              # Remove whitespace
s.isalpha()            # Check if alphabetic
s.join(['a', 'b'])     # "ahellob"
            """,
            'list': """
🎯 PRACTICAL EXAMPLES FOR list

# Creation
lst = [1, 2, 3]
lst = list(range(5))   # [0, 1, 2, 3, 4]

# Adding elements
lst.append(4)          # Add to end
lst.insert(0, 0)       # Insert at position
lst.extend([5, 6])     # Add multiple

# Removing elements
lst.pop()              # Remove last
lst.pop(0)             # Remove at index
lst.remove(3)          # Remove first occurrence
lst.clear()            # Remove all

# Accessing
lst[0]                 # First element
lst[-1]                # Last element
lst[1:3]               # Slice [start:end]

# Common operations
len(lst)               # Length
sorted(lst)            # Return sorted copy
lst.sort()             # Sort in place
lst.reverse()          # Reverse in place
lst.count(2)           # Count occurrences
            """,
            'dict': """
🎯 PRACTICAL EXAMPLES FOR dict

# Creation
d = {'a': 1, 'b': 2}
d = dict(a=1, b=2)

# Accessing
d['a']                 # Get value (KeyError if missing)
d.get('a', 0)          # Get with default
d.keys()               # All keys
d.values()             # All values
d.items()              # Key-value pairs

# Modifying
d['c'] = 3             # Add/update
d.update({'d': 4})     # Update multiple
del d['a']             # Delete key
d.pop('b')             # Remove and return
d.clear()              # Remove all

# Checking
'a' in d               # Check if key exists
d.setdefault('e', 5)   # Get or set default
            """,
            'set': """
🎯 PRACTICAL EXAMPLES FOR set

# Creation
s = {1, 2, 3}
s = set([1, 2, 2, 3])  # {1, 2, 3} - duplicates removed

# Adding/removing
s.add(4)               # Add element
s.update({5, 6})       # Add multiple
s.remove(1)            # Remove (KeyError if missing)
s.discard(1)           # Remove (no error)
s.pop()                # Remove arbitrary element

# Set operations
a = {1, 2, 3}
b = {2, 3, 4}
a | b                  # Union: {1, 2, 3, 4}
a & b                  # Intersection: {2, 3}
a - b                  # Difference: {1}
a ^ b                  # Symmetric difference: {1, 4}

# Checking
2 in s                 # Membership test
a.issubset(b)          # Is a subset?
a.issuperset(b)        # Is a superset?
            """,
            'int': """
🎯 PRACTICAL EXAMPLES FOR int

# Creation
x = 42
x = int("42")          # From string
x = int(3.14)          # From float (truncates)

# Operations
x + 5                  # Addition
x * 2                  # Multiplication
x ** 2                 # Power
x // 3                 # Floor division
x % 5                  # Modulo

# Conversions
bin(x)                 # Binary: "0b101010"
hex(x)                 # Hex: "0x2a"
oct(x)                 # Octal: "0o52"

# Bit operations
x & 15                 # Bitwise AND
x | 8                  # Bitwise OR
x ^ 3                  # Bitwise XOR
x << 2                 # Left shift
x >> 1                 # Right shift
            """,
            'tuple': """
🎯 PRACTICAL EXAMPLES FOR tuple

# Creation
t = (1, 2, 3)
t = 1, 2, 3            # Parentheses optional
t = (1,)               # Single element (comma required)

# Accessing
t[0]                   # First element
t[-1]                  # Last element
t[1:3]                 # Slice

# Operations
len(t)                 # Length
t.count(2)             # Count occurrences
t.index(3)             # Find index
t1 + t2                # Concatenate
t * 3                  # Repeat

# Unpacking
a, b, c = t            # Unpack to variables
a, *rest = t           # Unpack with remainder
            """
        }
        
        example = examples.get(self.current_type_name, f"No examples available for {self.current_type_name}")
        print(example)
    
    def inspect_method(self, method_name):
        """Inspect a specific method in detail."""
        if not self.current_type:
            print("⚠️  No type loaded. Please load a type first.")
            return
        
        if not hasattr(self.current_type, method_name):
            print(f"❌ Method '{method_name}' not found in type '{self.current_type_name}'")
            return
        
        method = getattr(self.current_type, method_name)
        
        print("\n" + "=" * 100)
        print(f"🔍 METHOD INSPECTION: {self.current_type_name}.{method_name}")
        print("=" * 100)
        
        # Signature
        try:
            sig = inspect.signature(method)
            print(f"\n📝 Signature:")
            print(f"  {self.current_type_name}.{method_name}{sig}")
        except:
            print(f"\n📝 Signature:")
            print(f"  {self.current_type_name}.{method_name}(...)")
        
        # Documentation
        doc = inspect.getdoc(method)
        if doc:
            print(f"\n📚 Documentation:")
            for line in doc.split('\n'):
                print(f"  {line}")
        else:
            print(f"\n📚 Documentation: None available")
    
    def compare_types(self, type_name1, type_name2):
        """Compare two built-in types."""
        if type_name1 not in self.builtin_types or type_name2 not in self.builtin_types:
            print("❌ One or both types not recognized")
            return
        
        type1 = self.builtin_types[type_name1]
        type2 = self.builtin_types[type_name2]
        
        methods1 = set(dir(type1))
        methods2 = set(dir(type2))
        
        common = methods1 & methods2
        only1 = methods1 - methods2
        only2 = methods2 - methods1
        
        print("\n" + "=" * 100)
        print(f"🔄 COMPARING: {type_name1} vs {type_name2}")
        print("=" * 100)
        
        print(f"\n✅ Common methods ({len(common)}):")
        for method in sorted(common):
            if not method.startswith('_'):
                print(f"  • {method}")
        
        print(f"\n📌 Only in {type_name1} ({len(only1)}):")
        for method in sorted(only1):
            if not method.startswith('_'):
                print(f"  • {method}")
        
        print(f"\n📌 Only in {type_name2} ({len(only2)}):")
        for method in sorted(only2):
            if not method.startswith('_'):
                print(f"  • {method}")
    
    def show_menu(self):
        """Show interactive menu."""
        print("\n" + "=" * 100)
        print("🎯 WHAT WOULD YOU LIKE TO DO?")
        print("=" * 100)
        print("\n  1. 🔍 Analyze a built-in type")
        print("  2. 💡 Show practical examples")
        print("  3. 🔎 Inspect a specific method")
        print("  4. 🔄 Compare two types")
        print("  5. 📋 List all available types")
        print("  6. ❌ Exit")
        
        choice = input("\n➤ Enter your choice (1-6): ").strip()
        return choice
    
    def interactive_mode(self):
        """Run the inspector in interactive mode."""
        while True:
            choice = self.show_menu()
            
            if choice == '1':
                self.list_available_types()
                type_name = input("\n➤ Enter type name: ").strip()
                if self.load_type(type_name):
                    self.analyze_type()
            
            elif choice == '2':
                if not self.current_type:
                    type_name = input("\n➤ Enter type name: ").strip()
                    if not self.load_type(type_name):
                        continue
                self.show_examples()
            
            elif choice == '3':
                if not self.current_type:
                    type_name = input("\n➤ Enter type name: ").strip()
                    if not self.load_type(type_name):
                        continue
                
                method_name = input("\n➤ Enter method name: ").strip()
                self.inspect_method(method_name)
            
            elif choice == '4':
                self.list_available_types()
                type1 = input("\n➤ Enter first type name: ").strip()
                type2 = input("➤ Enter second type name: ").strip()
                self.compare_types(type1, type2)
            
            elif choice == '5':
                self.list_available_types()
            
            elif choice == '6':
                print("\n👋 Thank you for using Built-in Type Inspector!")
                print("=" * 100)
                break
            
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 6.")


def main():
    """Main entry point."""
    print("\n" + "=" * 100)
    print("🐍 PYTHON BUILT-IN DATA TYPES INSPECTOR")
    print("=" * 100)
    print("\n✨ FEATURES:")
    print("  • Explore all built-in Python types")
    print("  • Categorized methods (query, mutation, conversion, operators)")
    print("  • Practical examples for each type")
    print("  • Compare different types")
    print("  • Detailed method inspection")
    print("\n💡 TIP: This is perfect for learning Python's core data structures!\n")
    
    inspector = BuiltinTypeInspector()
    
    if len(sys.argv) > 1:
        type_name = sys.argv[1]
        print(f"📦 Loading type from command line: {type_name}")
        if inspector.load_type(type_name):
            inspector.analyze_type()
            inspector.show_examples()
            inspector.interactive_mode()
        return
    
    inspector.interactive_mode()


if __name__ == "__main__":
    main()
