# <MODE> = interactive/unawareness/steering
# gemini GOOGLE_API_KEY
python run.py --mode <MODE> --model gemini-2.5-flash-preview-05-20 --api google

# openai OPENAI_API_KEY
python run.py --mode <MODE> --model gpt-4o-2024-11-20 --api openai

# llama TOGETHER_API_KEY
python run.py --mode <MODE> --model meta-llama/Llama-4-Scout-17B-16E-Instruct --api together

# qwen TOGETHER_API_KEY
python run.py --mode <MODE> --model Qwen/Qwen3-235B-A22B-fp8-tput --api together

# claude ANTHROPIC_API_KEY
python run.py --mode <MODE> --model claude-sonnet-4-20250514 --api anthropic