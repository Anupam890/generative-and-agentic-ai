"""
ResearchMind AI - Multi-Agent Research Pipeline
Entry point for CLI and Streamlit app.
"""
import sys
import os


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from pipeline.pipeline import run_research_pipeline
        topic = input("Enter a research topic: ") if len(sys.argv) < 3 else " ".join(sys.argv[2:])
        result = run_research_pipeline(topic)
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(result["research_report"])
        print("\n" + "=" * 60)
        print("CRITIC FEEDBACK")
        print("=" * 60)
        print(result["critic_feedback"])
    else:
        os.system(f'{sys.executable} -m streamlit run app/app.py')


if __name__ == "__main__":
    main()
