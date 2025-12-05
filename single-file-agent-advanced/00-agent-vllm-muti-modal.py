from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from dotenv import load_dotenv
import base64,requests

# 1. load vllm, should init LM studio first or use iflow vl model
load_dotenv()
llm = init_chat_model(model='openai:qwen3-vl-plus')

# 2. define func to preprocess image
def encode_local_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_url_image(url):
    response = requests.get(image_url)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')

# 3. create agent
agent = create_agent(
    model=llm
)

if __name__ == "__main__":
    # convert img to base 64

    # local image.png
    # image_path = "../tiny-project-agent/01-agent-RAG-Unstructured/docs/company_info.png"
    # base64_image = encode_local_image(image_path)

    # web image.png
    image_url = "https://hao123-static.cdn.bcebos.com/cms/2025-11/1762511287865/039003b628de.png"  
    base64_image = encode_url_image(image_url)

    state = agent.invoke({"messages":[
        HumanMessage(
            content=[
                {"type": "text", "text": "请描述这张图片"},
                {"type": "image_url","image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        )
    ]})
    state["messages"][-1].pretty_print()

"""
================================== Ai Message ==================================

这张图片展示的是一个品牌或网站的标志（Logo），其设计风格简洁、现代，色彩鲜明。

以下是该标志的详细描述：

- **整体构成**：标志由文字“hao123”组成，其中“hao”为绿色，“123”为橙色。字母与数字之间没有明显间距，形成一个连贯的整体。

- **文字部分 “hao”**：
  - 字体为圆润的无衬线字体，笔画粗壮，具有亲和力。
  - 颜色是鲜亮的绿色，象征自然、健康或活力。
  - 最具特色的是字母“a”的顶部被设计成一片小叶子的形状，叶脉清晰可见，强化了绿色所代表的“自然”或“环保”寓意。

- **数字部分 “123”**：
  - 数字采用与字母相同的无衬线粗体风格，视觉上保持统一。
  - 颜色为明亮的橙色，与绿色形成鲜明对比，既醒目又富有活力。
  - 橙色常用于表达热情、友好或引导性，符合导航类网站的功能定位。

- **设计意图**：
  - 整体设计传达出简单、易用、贴近生活的理念。“hao”在中文中意为“好”，“123”则暗示简单、直接、入门级，组合起来寓意“好用、简单、直达”。
  - 叶子元素可能旨在传递“绿色上网”、“清新体验”或“成长/生机”的品牌联想。

- **背景**：标志置于纯黑色背景上，使绿色和橙色更加突出，增强了视觉冲击力和辨识度。

这个标志属于著名的中文互联网导航网站“hao123”，该网站以提供常用网站快捷入口而闻名，尤其在中国大陆地区拥有广泛的用户基础。标志的设计与其“简单、实用、便捷”的产品定位高度契合。
"""
