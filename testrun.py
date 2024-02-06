import os
import re

def replace_static_urls(html_file_path):
    # Read the HTML file
    with open(html_file_path, "r") as file:
        html_content = file.read()

    # Define the directory paths for CSS and JS files
    css_directory = "static/css"
    js_directory = "static/js"

    # Find CSS file names in the HTML content
    css_file_names = re.findall(r'href="([^"]+\.css)"', html_content)
    # Replace CSS file names with the desired format
    for css_file_name in css_file_names:
        css_file_base = os.path.basename(css_file_name)  # Extract the file name

        if os.path.exists(os.path.join(css_directory, css_file_base)):
            css_url = "{{ url_for('static_css', path='" + css_file_base + "') }}"
            print(css_url)
            html_content = html_content.replace(css_file_name, css_url)

    # Find .download file names in the HTML content
    js_file_names = re.findall(r'src="([^"]+\.download)"', html_content)
    # Replace .download file names with the desired format
    for js_file_name in js_file_names:
        js_file_base = os.path.basename(js_file_name)

        if os.path.exists(os.path.join(js_directory, js_file_base)):
            js_url = "{{ url_for('static_js', path='" + js_file_base + "') }}"
            html_content = html_content.replace(js_file_name, js_url)

    return html_content

def write_modified_html(modified_html_content):
    with open("templates/licences.html", "w") as file:
        file.write(modified_html_content)

# Example usage:
html_file_path = "templates/cobalt-thank-you.html"
modified_html_content = replace_static_urls(html_file_path)

write_modified_html(modified_html_content)