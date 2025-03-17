#!/usr/bin/env python3
import nbformat
import sys
import os

def convert_notebook_to_mdx(notebook_path, mdx_path):
    # Read the notebook (assuming version 4)
    nb = nbformat.read(notebook_path, as_version=4)
    
    mdx_lines = []
    
    # Use the notebook metadata for the title if available, otherwise use a default title.
    title = nb.metadata.get('title', os.path.splitext(os.path.basename(notebook_path))[0])
    mdx_lines.append('---')
    mdx_lines.append(f"title: '{title}'")
    mdx_lines.append('---')
    mdx_lines.append('')  # blank line after frontmatter

    # Iterate over all the cells in the notebook.
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            # Write markdown cells as-is.
            mdx_lines.append(cell.source)
            mdx_lines.append('')
        elif cell.cell_type == 'code':
            # Write code cells wrapped in a code block with python language specifier.
            mdx_lines.append('```python')
            mdx_lines.append(cell.source)
            mdx_lines.append('```')
            mdx_lines.append('')
        # If needed, you can extend this to support other cell types.

    # Write the output to the MDX file.
    with open(mdx_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(mdx_lines))
    print(f"Conversion complete. MDX file saved to: {mdx_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_notebook_to_mdx.py <input_notebook.ipynb> [output_file.mdx]")
        sys.exit(1)

    notebook_path = sys.argv[1]
    mdx_path = sys.argv[2] if len(sys.argv) > 2 else 'output.mdx'
    convert_notebook_to_mdx(notebook_path, mdx_path)
