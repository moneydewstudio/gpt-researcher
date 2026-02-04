import streamlit as st
import os
from dotenv import load_dotenv
from gpt_researcher import GPTResearcher
import asyncio
import nest_asyncio
import re

nest_asyncio.apply()
load_dotenv()


def main():

    def sanitize_filename(query):
        """Sanitizes the query to be a valid filename."""
        return re.sub(r'[\s\W]+', '_', query)

    st.set_page_config(page_title="GPT Researcher", page_icon="🔎")
    st.title("GPT Researcher")
    st.markdown("This app allows you to conduct research using the GPT Researcher library.")

    query = st.text_input("Enter your research query:", 
                          placeholder="e.g., What are the latest trends in artificial intelligence?")

    report_type = st.selectbox("Select report type:",
                               ["research_report", "resource_report", "outline_report", "custom_report",
                                "subtopic_report", "variable_report"])

    if st.button("Research"):
        if query:
            st.write(f"Conducting research for: {query}")

            async def research():
                custom_prompt = """
                **Research Topic:** The definition of a particular term in the scope of social science, sourced only using peer reviewed papers.

                **Objective:** To provide a comprehensive overview of the term, including its definitions, theories, indicators, measurements, related research, and APA style references.

                **Report Structure:**
                1.  **Introduction:**
                    *   Define the term and its significance in social science.
                2.  **Definition:**
                    *   Provide definitions of the term based on theories and researchers.
                3.  **Indicators:**
                    *   Identify and describe the key indicators used to measure or identify the term.
                4.  **Related Research:**
                    *   Summarize key research findings related to the term in the past 10 years.
                    *   Discuss any debates or controversies in the literature.
                5.  **Conclusion:**
                    *   Summarize the main points of the report.
                    *   Suggest areas for future research.
                6.  **References:**
                    *   Provide a list of all cited sources in APA style.
                """

                variable_report_prompt = f"""
**Research Task:** Generate a detailed research report for the variable: **"{query}"**.

**Objective:** To provide a comprehensive overview of the variable, including its definitions, theoretical background, indicators, related research, and references in APA style.

**Report Structure:** You MUST follow this exact markdown format:

# {query}
## Definitions and theories of {query}
### Indicators of {query}
## Researches on {query}
### Scales and Measurements of {query}
### Future research for {query}
## References for {query}
"""
                if report_type == "custom_report":
                    researcher = GPTResearcher(query=query, report_type=report_type, config_path=None,
                                               source_urls=None, custom_prompt=custom_prompt)
                elif report_type == "variable_report":
                    researcher = GPTResearcher(query=query, report_type="custom_report", config_path=None,
                                               source_urls=None, custom_prompt=variable_report_prompt)
                else:
                    researcher = GPTResearcher(query=query, report_type=report_type)
                
                research_result = await researcher.conduct_research()
                report = await researcher.write_report()
                return report
            
            report = asyncio.run(research())
            st.download_button(
                label="Download",
                data=report,
                file_name=f"{sanitize_filename(query)}.md",
            )
            st.markdown(report)
        else:
            st.warning("Please enter a research query.")

if __name__ == "__main__":
    main()
