import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import html2text
import requests

class MessageHandle:
    def extract_url_from_wechat_xml(self, xml_content):
        try:
            # 解析XML内容
            root = ET.fromstring(xml_content)
            
            # 查找<url>元素
            url_element = root.find('.//url')
            
            if url_element is not None:
                return url_element.text
            else:
                return "URL not found in the XML content"
        except ET.ParseError:
            return "Invalid XML content"
        except Exception as e:
            return f"An error occurred: {str(e)}"
    

class FileHandle:
    def webpage_to_markdown(self,url):
        # Fetch the webpage content
        response = requests.get(url)
        html_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unnecessary elements (you may need to adjust this based on the specific webpage structure)
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()

        # Convert HTML to Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        markdown_content = h.handle(str(soup))

        return markdown_content

# Usage
url = "https://mp.weixin.qq.com/s?t=pages/image_detail&scene=1&__biz=MzkxNzY4MTUwNA==&mid=2247487104&idx=2&sn=bca37767d8a93ef9310b66b36678c1d9&sharer_shareinfo_first=133e78d7c699e50be8319a5127e3145d&sharer_shareinfo=133e78d7c699e50be8319a5127e3145d#wechat_redirect"

file_handle = FileHandle()
markdown = file_handle.webpage_to_markdown(url)


# Save the markdown content to a file
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(markdown)

print("Conversion complete. Check 'output.md' for the result.")
