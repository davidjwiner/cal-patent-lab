# cal-patent-lab: Predicting Bad Patents

Engineering 296 Capstone Project, 2016-2017
University of California, Berkeley

This is a machine learning project aimed at tackling an issue with "bad patents", whereby new patent filings with a high level of similarity to older filings cause disputes which in turn cause significant wastage of time and money on litigation in court. If every new patent filing could be compared against an entire database of older patents before a decision is made, that would solve the issue, but the sheer number of patents in existence make this unfeasible if using humans. Machine learning, on the other hand, allows such actions to be fully automated, and thus presents a viable solution to the problem. From August to April, we developed a multi-part software solution involving large-scale data retrieval and analysis, the implementation and training of a support vector machine learning model, and the creation of an interactive graphical user interface.

Overview of Folders:

* **csv**: Contains USPTO data in tabular format
* **html**: Extracted web pages from eFOIA, utilized by our parsing scripts
* **lib**: Contains our parsing scripts and Jupyter notebooks
* **patentGUI**: PatentCheck, our Django-based web app for executing the algorithms
* **ptab-raw-pdf**: Downloaded patent text from eFOIA, in original PDF format
* **ptab-raw-text**: Raw text extracted fromeFOIA PDF files

Important Note for Developers:
* Every time you add a requirement to a python script (e.g., `import numpy as np`), make sure you add that requirement to the requirements file in `lib/requirements.txt`
* Run the requirements files to get all the latest dependencies with `python -m pip install -r requirements.txt`