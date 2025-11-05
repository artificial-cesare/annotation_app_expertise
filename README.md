# Streamlit Annotation App

This project is a Streamlit application designed to collect human expertise annotations on speeches. The application allows users to view sampled speeches and submit their annotations, which are then saved in a CSV file for further analysis.

## Project Structure

```
streamlit-annotation-app
├── src
│   ├── app.py                  # Main entry point of the Streamlit application
│   ├── utils
│   │   └── data_handler.py     # Utility functions for data operations
│   └── components
│       ├── speech_viewer.py    # Component for displaying speech text and context
│       └── annotation_form.py   # Component for collecting user annotations
├── data
│   ├── sampled_speeches.json    # Sampled speeches data in JSON format
│   └── annotations.csv           # CSV file to store collected annotations
├── requirements.txt              # List of dependencies for the project
├── .gitignore                    # Files and directories to ignore by Git
└── README.md                     # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd streamlit-annotation-app
   ```

2. **Install dependencies:**
   It is recommended to create a virtual environment before installing the dependencies.
   You can do so by running this command in your terminal:
   ```
   conda create -n annotation-env python=3.13
   ```
   then activate the environment:
   ```
   conda activate annotation-env
   ```
   Then, install the required packages using pip:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application:**
   Once you have installed the dependencies, with the environment activated, you can start the Streamlit application by navigating to the "streamlit-annotation-app" directory and running:
   ```
   streamlit run src/app.py
   ```

## Usage Guidelines

- Upon running the application, users will be presented with a list of speeches to review.
- Users can read the speech text and context before providing their annotations.
- The annotation form collects the following information:
  - **Rater ID:** Identifier for the user providing the annotation.
  - **Score:** A numerical score representing the expertise level.
  - **Justification:** A text field for the user to explain their score.
  - **Context:** The context of the speech being annotated.
  - **Statement:** The actual speech text.

## Contribution

Contributions to the project are welcome. Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.