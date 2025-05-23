import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI # Used for Gemini with a custom base_url
import gradio as gr
import json

# Load environment variables from .env file
load_dotenv(override=True)
google_api_key = os.getenv('GOOGLE_API_KEY')

# Configure the OpenAI client to use the Google Generative Language API
# This setup allows using a Gemini model via an OpenAI-compatible endpoint
MODEL = "gemini-2.0-flash-exp" # Or your desired Gemini model
gemini = OpenAI(
    api_key=google_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Headers for web requests to mimic a browser
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    """
    A utility class to represent a Website that has been scraped.
    It fetches the content of a given URL, parses its HTML to extract
    the title and main text content, after removing irrelevant tags.
    Handles potential errors during fetching or parsing.
    """
    def __init__(self, url):
        """
        Initializes the Website object by fetching and parsing the content from the given URL.

        Args:
            url (str): The URL of the website to scrape.
        """
        self.url = url
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            self.body = response.content
            soup = BeautifulSoup(self.body, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"
            
            # Remove irrelevant tags like script, style, img, input for cleaner text
            if soup.body:
                for irrelevant in soup.body(["script", "style", "img", "input", "nav", "footer", "aside"]):
                    irrelevant.decompose()
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = "No body content found."
        except requests.RequestException as e:
            self.title = "Error fetching title"
            self.text = f"Error fetching website content: {e}"
        except Exception as e:
            self.title = "Error parsing title"
            self.text = f"Error parsing website content: {e}"


    def get_contents(self):
        """
        Returns a formatted string containing the title and text content of the webpage.
        
        Returns:
            str: A string with the webpage title and its main textual content.
        """
        return f"Webpage Title:\n{self.title}\n\nWebpage Contents:\n{self.text}\n\n"

# System prompts for the AI model
SYSTEM_PROMPT_ENG = """You are an assistant that analyzes the contents of a company's landing page
and creates a short, engaging brochure about the company for prospective customers, investors, and recruits.
Respond in markdown. Focus on key information like what the company does, its mission, and its unique selling points.
If available, briefly mention company culture, customers, or career opportunities.
Structure the brochure clearly with headings and bullet points where appropriate."""

SYSTEM_PROMPT_THAI = """คุณเป็นผู้ช่วย AI ที่วิเคราะห์เนื้อหาจากหน้า Landing Page ของบริษัท
และสร้างโบรชัวร์สั้นๆ เกี่ยวกับบริษัทสำหรับลูกค้าเป้าหมาย นักลงทุน และผู้สนใจร่วมงาน
โปรดตอบเป็นภาษาไทยในรูปแบบ Markdown เน้นข้อมูลสำคัญ เช่น บริษัททำอะไร พันธกิจคืออะไร และจุดขายที่เป็นเอกลักษณ์คืออะไร
หากมีข้อมูลเกี่ยวกับวัฒนธรรมองค์กร ลูกค้า หรือโอกาสในการร่วมงาน โปรดกล่าวถึงสั้นๆ
จัดโครงสร้างโบรชัวร์ให้ชัดเจน ใช้หัวข้อและสัญลักษณ์แสดงหัวข้อย่อยตามความเหมาะสม"""

def stream_gemini(system_prompt, user_prompt):
    """
    Sends a request to the Gemini model via the OpenAI-compatible API and streams the response.

    Args:
        system_prompt (str): The system message to guide the AI's behavior.
        user_prompt (str): The user's message or query to the AI.

    Yields:
        str: Chunks of the AI's response as they are generated.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ]
    
    # Limit the user_prompt length to avoid exceeding token limits (approximate)
    max_chars_user_prompt = 15000 
    if len(user_prompt) > max_chars_user_prompt:
        user_prompt = user_prompt[:max_chars_user_prompt] + "\n[Content truncated due to length]"
        messages[1]["content"] = user_prompt

    stream_response = gemini.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )
    response_text = ""
    for chunk in stream_response:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content
            yield response_text
        elif chunk.choices and chunk.choices[0].finish_reason == "error":
            error_message = f"\n\n[Error from API: {chunk.choices[0].error_message if hasattr(chunk.choices[0], 'error_message') else 'Unknown error'}]"
            response_text += error_message
            yield response_text
            return


def stream_brochure(company_name, url, version):
    """
    Generates a company brochure by fetching content from the given URL and
    using the Gemini model to create the brochure text based on the selected language.
    It streams the brochure content.

    Args:
        company_name (str): The name of the company.
        url (str): The URL of the company's landing page.
        version (str): The desired language for the brochure ("English" or "Thai").

    Yields:
        str: Chunks of the generated brochure in Markdown format.
    """
    if not company_name or not url:
        yield "Please enter both company name and URL."
        return

    if not (url.startswith("http://") or url.startswith("https://")):
        yield "Please enter a valid URL including http:// or https://"
        return

    website_data = Website(url)
    if "Error fetching website content" in website_data.text or "Error parsing website content" in website_data.text:
        yield f"Could not retrieve content from the URL: {url}\nDetails: {website_data.text}"
        return
        
    user_prompt_content = f"Please generate a company brochure for '{company_name}'. Here is the content from their landing page ({url}):\n\n"
    user_prompt_content += website_data.get_contents()

    active_system_prompt = SYSTEM_PROMPT_THAI if version == "Thai" else SYSTEM_PROMPT_ENG
    
    yield from stream_gemini(active_system_prompt, user_prompt_content)

# Main execution block to launch the Gradio app
if __name__ == "__main__":
    # This block defines and launches the Gradio user interface
    with gr.Blocks(theme=gr.themes.Glass(), css="footer {display: none !important}") as view:
        gr.Markdown(
            """
            # 🚀 AI Brochure Generator
            Enter the company details below to generate a personalized brochure.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                company_name_input = gr.Textbox(
                    label="Company Name:",
                    placeholder="e.g., Innovatech Solutions",
                    info="The official name of the company."
                )
                landing_page_url_input = gr.Textbox(
                    label="Landing Page URL:",
                    placeholder="e.g., https://www.innovatech.com",
                    info="Must include http:// or https://"
                )
                version_input = gr.Dropdown(
                    ["English", "Thai"],
                    label="Select Language Version",
                    value="English",
                    info="Choose the language for the brochure."
                )
                submit_button = gr.Button("Generate Brochure", variant="primary")

            with gr.Column(scale=2):
                brochure_output = gr.Markdown(label="Generated Brochure:")

        submit_button.click(
            fn=stream_brochure,
            inputs=[company_name_input, landing_page_url_input, version_input],
            outputs=[brochure_output]
        )
        

    print("Launching Gradio App...")
    # Set share=True if you want to create a public link (requires internet and frpc setup)
    # Set inbrowser=True to automatically open the app in your default web browser
    view.launch(inbrowser=True)
