import requests
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from LLM import vl_llm


# config
# BASE_URL = 
# API_KEY = vl_llm.openai_api_key    # not needed for local deploy model
# MODEL_ID = vl_llm.model_name

# perpare LM studio
def check_LM_studio(key_word="vl"):
    resp = requests.get(f"{vl_llm.openai_api_base}models", timeout=5)
    model_data = resp.json().get("data")
    vl_models = [m["id"] for m in model_data if key_word in m["id"]]
    return vl_models

# 1. Create Convert
# 1.1 init pipeline
pipeline_options = VlmPipelineOptions(enable_remote_services=True)
pipeline_options.vlm_options = ApiVlmOptions(
    url=f"{vl_llm.openai_api_base}chat/completions",
    params=dict(model=vl_llm.model_name, max_tokens=1024 * 4),
    headers={"Authorization":f"Bearer {vl_llm.openai_api_key}"} if vl_llm.openai_api_key else {},
    prompt="Please convert this document page to clean markdown format. Extract all text, tables, and structure accurately.",
    temperature=0.1,
    response_format=ResponseFormat.MARKDOWN  # 使用具体的枚举值
)
# 1.2 create converter
converter = DocumentConverter(
    allowed_formats=[
        InputFormat.MD,InputFormat.PDF,InputFormat.IMAGE,
        InputFormat.DOCX,InputFormat.XLSX,InputFormat.PPTX
    ],
    format_options={
        # PDF and IMAGE will use VLM to convert
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
            pipeline_cls=VlmPipeline,
        ),
        InputFormat.IMAGE: ImageFormatOption(
            pipeline_options=pipeline_options,
            pipeline_cls=VlmPipeline,
        )
        # other formats will use standard processing
    }
)

if __name__ == "__main__":
    check_LM_studio()

    # res = converter.convert('./docs/monthly_sales_data.xlsx')
    # res = converter.convert('./docs/sales_strategy_report.docx')
    # res = converter.convert('./docs/market_analysis.pptx')

    # use vl-model to convert
    # res = converter.convert('./docs/product_catalog.pdf')
    res = converter.convert('./docs/company_info.png')
    print(res.document.export_to_text())