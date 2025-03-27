# Financial Assistant

Financial Assistant is a web application designed to help users manage their finances, optimize their budgets, and make informed investment decisions. The application uses Bayesian models to predict individual incomes based on demographic data and provides various tools and insights for financial planning.

## Features

- **Income Prediction**: Predict individual incomes using Bayesian posterior weights from zipcode-level models.
- **Budget Optimization**: Insights and tools to help users optimize their monthly budgets.
- **Investment Ideas**: Information and tools to help users make informed investment decisions.
- **Dynamic Graphs**: Visual representations of financial data to help users understand their financial situation better.

## Technologies Used

- **Python**: For backend data processing and Bayesian modeling.
- **JavaScript**: For frontend development.
- **React**: For building the user interface.
- **Material-UI**: For UI components.
- **React Spring**: For animations.
- **React Awesome Reveal**: For scroll-triggered animations.
- **Pandas**: For data manipulation and analysis.
- **PyMC3**: For Bayesian modeling.
- **Tabulate**: For displaying data in tabular format.

## Project Structure

- `src/component/data_part.py`: Contains the data processing and Bayesian modeling logic.
- `src/Data/Data_synthesizer.py`: Script for synthesizing individual income data.
- `src/app/src/App.js`: Main React application file.
- `src/app/src/pages/HomePage.js`: Home page component of the React application.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/aman-jaglan/financial-assistant.git
    cd financial-assistant
    ```

2. **Backend Setup**:
    - Create a virtual environment and activate it:
      ```sh
      python -m venv venv
      source venv/bin/activate  # On Windows use `venv\Scripts\activate`
      ```
    - Install the required Python packages:
      ```sh
      pip install -r requirements.txt
      ```

3. **Frontend Setup**:
    - Navigate to the `src/app` directory:
      ```sh
      cd src/app
      ```
    - Install the required npm packages:
      ```sh
      npm install
      ```

## Usage

1. **Data Processing**:
    - Run the data synthesizer script to generate synthetic individual income data:
      ```sh
      python src/Data_Synthesizer/customer_synthesizer.py
      ```

2. **Start the Frontend**:
    - In the `src/app` directory, start the React development server:
      ```sh
      npm start
      ```

3. **Access the Application**:
    - Open your web browser and navigate to `http://localhost:3000` to access the Financial Assistant application.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or inquiries, please contact [aman-jaglan](https://github.com/aman-jaglan).
