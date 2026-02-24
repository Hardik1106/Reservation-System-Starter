import os
import re

def parse_java_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Simple cleanups
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    package = ""
    pkg_match = re.search(r'package\s+([\w\.]+);', content)
    if pkg_match:
        package = pkg_match.group(1)

    # Find class/interface/enum
    # Support public abstract class etc.
    class_pattern = re.compile(r'(public|protected|private)?\s*(abstract)?\s*(class|interface|enum)\s+(\w+)\s*(extends\s+\w+)?\s*(implements\s+[\w\s,]+)?\s*\{', re.MULTILINE)
    
    classes = []
    for match in class_pattern.finditer(content):
        type_ = match.group(3)
        name = match.group(4)
        extends_raw = match.group(5)
        implements_raw = match.group(6)
        
        extends = extends_raw.replace('extends', '').strip() if extends_raw else ""
        implements = [i.strip() for i in implements_raw.replace('implements', '').split(',')] if implements_raw else []
        
        # very basic body extraction
        body_start = match.end()
        brace_count = 1
        body_end = body_start
        for i in range(body_start, len(content)):
            if content[i] == '{': brace_count += 1
            elif content[i] == '}': brace_count -= 1
            if brace_count == 0:
                body_end = i
                break
                
        body = content[body_start:body_end]
        
        fields = []
        methods = []
        
        if type_ != 'enum':
            # extract fields: something like "private String name;"
            # extremely simplified 
            lines = body.split(';')
            for line in lines:
                line = line.strip()
                if not line or '{' in line or '}' in line or '=' in line and '(' in line: continue # method or initialized 
                if '(' in line: continue # method
                
                parts = line.split()
                if len(parts) >= 2:
                    # heuristic for fields
                    if parts[0] in ['public', 'private', 'protected']:
                        modifiers = parts[0]
                        typ = parts[1]
                        name_ = parts[-1]
                        fields.append((modifiers, typ, name_))
                        
            # extract methods: extremely simplifield "public void foo() {"
            method_pattern = re.compile(r'(public|private|protected)\s+([\w<>\[\]]+)\s+(\w+)\s*\([^)]*\)')
            for m in method_pattern.finditer(body):
                methods.append((m.group(1), m.group(2), m.group(3)))
                
        classes.append({
            'package': package,
            'type': type_,
            'name': name,
            'extends': extends,
            'implements': implements,
            'fields': fields,
            'methods': methods,
            'enum_body': body if type_ == 'enum' else ""
        })
        
    return classes

def write_puml(classes_data, out_file):
    with open(out_file, 'w') as f:
        f.write("@startuml\n")
        f.write("skinparam classAttributeIconSize 0\n")
        f.write("left to right direction\n\n")
        
        # declare classes
        for cls in classes_data:
            if cls['type'] == 'enum':
                f.write(f"enum {cls['name']} {{\n")
                enum_items = [x.strip() for x in cls['enum_body'].split(',') if x.strip()]
                for item in enum_items:
                    clean_item = item.split(';')[0].split('{')[0].strip()
                    if clean_item and not " " in clean_item:
                        f.write(f"  {clean_item}\n")
                f.write("}\n")
            else:
                f.write(f"{cls['type']} {cls['name']} {{\n")
                for mod, typ, name in cls['fields']:
                    symbol = "+" if mod == "public" else "-" if mod == "private" else "#"
                    f.write(f"  {symbol}{name} : {typ}\n")
                for mod, typ, name in cls['methods']:
                    symbol = "+" if mod == "public" else "-" if mod == "private" else "#"
                    f.write(f"  {symbol}{name}() : {typ}\n")
                f.write("}\n")
                
        f.write("\n")
                
        # declare relationships
        for cls in classes_data:
            if cls['extends']:
                f.write(f"{cls['extends']} <|-- {cls['name']}\n")
            
            for impl in cls['implements']:
                f.write(f"{impl} <|.. {cls['name']}\n")
                
            # associations from fields
            for mod, typ, name in cls['fields']:
                clean_typ = typ.replace('List<', '').replace('>', '').replace('[]', '').strip()
                if any(clean_typ == c['name'] for c in classes_data if c['name'] != cls['name']):
                    f.write(f"{cls['name']} --> {clean_typ}\n")
                    
        f.write("@enduml\n")

def main():
    import glob
    src_dir = '/Users/va/SE takehome 2/Reservation-System-Starter/src/main/java'
    java_files = glob.glob(src_dir + '/**/*.java', recursive=True)
    
    all_classes = []
    for f in java_files:
        all_classes.extend(parse_java_file(f))
        
    write_puml(all_classes, 'class_diagram.puml')
    print("Generated class_diagram.puml")

if __name__ == "__main__":
    main()
