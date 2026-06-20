import os
import shutil
import re
import yaml

# Configurations
CONFIG_FILE = 'course.yaml'
DOCS_DIR = 'docs'
MKDOCS_YML = 'mkdocs.yml'

# Group mappings
GROUPS = {
    'Getting Started': ['ch01', 'ch02', 'ch03', 'ch04', 'ch05'],
    'Core Syntax': ['ch06', 'ch07', 'ch08', 'ch09', 'ch10'],
    'Data Structures & Built-ins': ['ch11', 'ch12', 'ch13', 'ch14', 'ch15'],
    'Infrastructure Automation': ['ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21']
}

def clean_emoji_and_tags(text):
    # Remove emoji like 📁, 🧠, 🕵️, etc. and strip whitespace
    cleaned = re.sub(r'[^\x00-\x7F]+', '', text)
    return cleaned.strip(' #/-📁\t\n\r')

def extract_metadata(file_path):
    """
    Extracts category path and clean title from the top headers of a markdown file.
    Example:
    Line 1: # 📁 Setting Up Your Python Environment / 📁 Installing Python
    Line 2: ## 📁 What is Python and History of Python
    """
    category = "Python Course"
    title = "Lesson"
    content_lines = []
    
    if not os.path.exists(file_path):
        return category, title, ""

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    header_found = 0
    for line in lines:
        if line.startswith('# ') and header_found == 0:
            category = clean_emoji_and_tags(line)
            header_found = 1
        elif line.startswith('## ') and header_found == 1:
            title = clean_emoji_and_tags(line)
            header_found = 2
        else:
            # Add remaining lines to content
            if header_found == 2:
                content_lines.append(line)
            else:
                # If headers are missing/malformed, just append everything
                content_lines.append(line)
                
    content = "".join(content_lines).strip()
    return category, title, content

def indent_content(content):
    return '\n'.join(f"    {line}" for line in content.splitlines())

def build_portal():
    # Source paths (relative to doc_engine_rtd folder)
    theory_dir = "../project_21_repo/theory_for_student/theory_for_student_md_file_to_read"
    code_dir = "../project_21_repo/code_for_student/code_for_student_md_file_to_read"
    
    # 1. Recreate docs directory
    if os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, 'stylesheets'), exist_ok=True)
    # Write extra.css stylesheet
    css_content = """/* 1. Full Screen Width Reading Panel */
.wy-nav-content-wrap {
    max-width: none !important;
    width: auto !important;
    float: none !important;
}
.wy-nav-content {
    max-width: none !important;
    width: 100% !important;
}

/* 2. Left Panel Link Single Line Truncation */
.wy-menu-vertical li a {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* 3. Sleek inline tag styling */
.category-tag {
    font-size: 0.85em;
    color: #777777;
    margin-top: -10px;
    margin-bottom: 20px;
    display: inline-block;
}

/* 4. Tabbed Panel styling (Theory/Code) */
.tabbed-set {
    display: flex;
    flex-wrap: wrap;
    position: relative;
    margin: 1.5em 0 2em;
}
.tabbed-set > input {
    display: none;
}
.tabbed-labels {
    display: flex;
    width: 100%;
    border-bottom: 2px solid #e1e4e5;
    margin-bottom: 1.5em;
}
.tabbed-labels > label {
    padding: 12px 24px;
    cursor: pointer;
    font-weight: bold;
    color: #555555;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s ease-in-out;
    user-select: none;
}
.tabbed-labels > label:hover {
    color: #2980b9;
}
.tabbed-content {
    width: 100%;
}
.tabbed-block {
    display: none;
}

/* Toggle Visibility and Active Tab Styling */
.tabbed-set > input:nth-of-type(1):checked ~ .tabbed-labels > label:nth-of-type(1),
.tabbed-set > input:nth-of-type(2):checked ~ .tabbed-labels > label:nth-of-type(2),
.tabbed-set > input:nth-of-type(3):checked ~ .tabbed-labels > label:nth-of-type(3) {
    color: #2980b9;
    border-bottom: 2px solid #2980b9;
}
.tabbed-set > input:nth-of-type(1):checked ~ .tabbed-content > .tabbed-block:nth-of-type(1),
.tabbed-set > input:nth-of-type(2):checked ~ .tabbed-content > .tabbed-block:nth-of-type(2),
.tabbed-set > input:nth-of-type(3):checked ~ .tabbed-content > .tabbed-block:nth-of-type(3) {
    display: block;
}
"""
    with open(os.path.join(DOCS_DIR, 'stylesheets', 'extra.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)

    # 2. Scrape and process all markdown files
    files = sorted([f for f in os.listdir(theory_dir) if f.endswith('.md')])
    
    grouped_lessons = {g: [] for g in GROUPS.keys()}
    
    for filename in files:
        # Match pattern: ch01_01_01-what-is-python-and-history.md
        match = re.match(r'(ch\d+)_(\d+)_(\d+)-(.*)\.md', filename)
        if not match:
            continue
            
        ch_num = match.group(1)
        sec_num = match.group(2)
        seq_num = match.group(3)
        
        # Determine group
        group_name = None
        for g_name, prefixes in GROUPS.items():
            if ch_num in prefixes:
                group_name = g_name
                break
        if not group_name:
            continue
            
        theory_path = os.path.join(theory_dir, filename)
        code_path = os.path.join(code_dir, filename)
        
        # Extract title and contents
        category, title, theory_text = extract_metadata(theory_path)
        
        # Determine output filename
        safe_group_dir = os.path.join(DOCS_DIR, group_name)
        os.makedirs(safe_group_dir, exist_ok=True)
        
        target_filename = f"{ch_num}_{sec_num}_{seq_num}.md"
        target_path = os.path.join(safe_group_dir, target_filename)
        
        # Compile content based on whether a matching code file exists
        if os.path.exists(code_path):
            _, _, code_text = extract_metadata(code_path)
            
            # Add a dynamic callout/tip at the bottom of theory to guide the student
            theory_text_with_tip = theory_text + "\n\n!!! info \"Interactive Views\"\n    You are currently in **📚 All-in-One** mode. Use the tabs at the top to switch to **📖 Theory Only** or **💻 Code Only** views."
            
            combined_md = f"# {title}\n"
            combined_md += f'<span class="category-tag">🏷️ {category}</span>\n\n'
            combined_md += f'=== "📚 All-in-One"\n{indent_content(theory_text)}\n\n    ---\n\n{indent_content(code_text)}\n\n'
            combined_md += f'=== "📖 Theory Only"\n{indent_content(theory_text_with_tip)}\n\n'
            combined_md += f'=== "💻 Code Only"\n{indent_content(code_text)}\n'
        else:
            # Standard page layout without tabs (e.g. for future non-coding lessons)
            combined_md = f"# {title}\n"
            combined_md += f'<span class="category-tag">🏷️ {category}</span>\n\n'
            combined_md += theory_text
            
        # Format the lesson name for nav, keeping it clean: e.g. "Ch 01 | What is Python & History"
        ch_label = f"Ch {ch_num[2:]}"
        nav_title = f"{ch_label} | {title}"

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(combined_md)
            
        grouped_lessons[group_name].append({
            'nav_title': nav_title,
            'title': title,
            'chapter': ch_num,
            'path': f"{group_name}/{target_filename}"
        })

    # 3. Create landing pages (roadmaps) for each grouping
    for group_name, lessons in grouped_lessons.items():
        roadmap_content = f"# {group_name} Roadmap\n"
        roadmap_content += f'<span class="category-tag">🏷️ Course Modules</span>\n\n'
        roadmap_content += "Welcome to the module! Below is the complete roadmap of chapters and lessons. Click any topic to get started.\n\n"
        
        # Group by chapter number
        current_ch = None
        for lesson in lessons:
            ch_num = lesson['chapter']
            if ch_num != current_ch:
                current_ch = ch_num
                # Capitalize chapter title nicely
                roadmap_content += f"\n### Chapter {current_ch[2:].lstrip('0')}\n"
                roadmap_content += "---\n"
            
            # Add lesson link
            roadmap_content += f"* [{lesson['title']}]({os.path.basename(lesson['path'])})\n"
            
        group_index_path = os.path.join(DOCS_DIR, group_name, "index.md")
        with open(group_index_path, 'w', encoding='utf-8') as f:
            f.write(roadmap_content)

    # Create root homepage with rich content
    root_index_path = os.path.join(DOCS_DIR, "index.md")
    homepage_content = """# Python Ali

## Learn Python the Structured Way. From Zero to Real-World Automation.

Join over 2 million learners who have mastered Python. Whether you are writing your very first line of code or an IT infrastructure engineer looking to automate your daily workflows, we have the roadmap you need.

<div style="margin: 30px 0;">
    <a href="Getting Started/" style="background-color: #000000 !important; color: #ffffff !important; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 1.1em; border: 1px solid #000000;">🚀 Start Learning for Free</a>
</div>

---

### 👥 Built by Engineers, for Everyone

When we—**Vivek Kumar**, **Adharsh Murukesan**, and **Hari Krishnan**—first decided to learn Python, we hit a wall. We were drowning in tutorials but couldn't find a clear, structured curriculum to take us from absolute beginners to capable IT infrastructure engineers who can automate daily operational tasks.

Instead of giving up, we built the roadmap we wished we had. What started as a personal project to organize our own learning has grown into a platform trusted by over **2,000,000 users**. We believe that high-quality tech education should be accessible, which is why this entire curriculum is—and always will be—completely free to use.

---

### 💡 Trust the Process

Learning to code is a journey. You might find some concepts difficult to grasp at first, and that is completely normal. Our philosophy is simple: **trust the process and keep practicing**.

We have packed this curriculum with hands-on examples and real-world scenarios. Don't just read the code—type it out, break it, and fix it. Stick with it, and the complex topics will become second nature.

---

### 🎯 A Curriculum for Beginners and Professionals Alike

* **The Absolute Beginner**: No coding experience? No problem. We start at zero, walking you through the fundamentals of programming in a clear, logical sequence.
* **The IT Infrastructure Engineer**: If you work in IT infrastructure, Python is your superpower. We include practical examples tailored to the field, showing you how to move past manual configurations. You will learn how to write scripts that actually save you time on the job—such as automating interactive IP and hostname resolution across your network.
"""
    with open(root_index_path, 'w', encoding='utf-8') as f:
        f.write(homepage_content)

    # 4. Generate mkdocs.yml configuration
    nav_structure = []
    
    # Root entry
    nav_structure.append({"Home": "index.md"})
    
    # Python Course
    python_nav = []
    for group_name, lessons in grouped_lessons.items():
        group_nav = []
        # First entry in each group is its roadmap/landing page
        group_nav.append({f"{group_name} Roadmap": f"{group_name}/index.md"})
        for lesson in lessons:
            group_nav.append({lesson['nav_title']: lesson['path']})
        python_nav.append({group_name: group_nav})
        
    nav_structure.append({"Python for Infrastructure": python_nav})
    
    # Java Course Placeholder
    coming_soon_dir = os.path.join(DOCS_DIR, "Java for Infrastructure")
    os.makedirs(coming_soon_dir, exist_ok=True)
    coming_soon_path = os.path.join(coming_soon_dir, "coming_soon.md")
    with open(coming_soon_path, 'w', encoding='utf-8') as f:
        f.write("# Coming Soon\n\nThis course is currently in development. Stay tuned!\n")
        
    nav_structure.append({"Java for Infrastructure": [
        {"Getting Ready": [
            {"Coming Soon": "Java for Infrastructure/coming_soon.md"}
        ]}
    ]})

    mkdocs_config = {
        'site_name': 'Python Ali',
        'site_url': 'https://pythonali.com',
        'theme': {
            'name': 'readthedocs',
            'highlightjs': True,
            'hljs_languages': ['python', 'yaml', 'bash']
        },
        'extra_css': ['stylesheets/extra.css'],
        'markdown_extensions': [
            'admonition',
            'pymdownx.superfences',
            {
                'pymdownx.tabbed': {
                    'alternate_style': True
                }
            }
        ],
        'nav': nav_structure
    }

    with open(MKDOCS_YML, 'w', encoding='utf-8') as f:
        yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
        
    print("Portal generated successfully!")

if __name__ == '__main__':
    build_portal()
