
# AI-Powered Telephone Ordering System

An AI-powered automated telephone ordering system developed as part of a diploma thesis at the University of Patras, Greece.

The system enables customers to place coffee orders over the phone using natural language, while allowing staff to review and manage orders through a dashboard.

## 🎓 Diploma Thesis

**Title:** Design and Development of an Automated Telephone Ordering System Using Artificial Intelligence

**Institution:** University of Patras  
**Department:** Electrical and Computer Engineering

## 🚀 Project Overview

The application combines speech recognition, natural language processing, database-driven menu retrieval, and automated order processing to streamline telephone ordering for coffee shops.

### Key Features

- Automated telephone interactions using Vonage.
- Speech-to-text transcription using OpenAI Whisper.
- Natural language order extraction using GPT-4o-mini.
- Dynamic menu retrieval from an SQLite database.
- Order validation before database persistence.
- Dashboard for staff to review and manage orders.
- Multi-store support through store-specific data.

## 🛠️ Technologies Used

- **Python** — Backend development.
- **FastAPI** — API and application backend.
- **SQLite** — Relational database.
- **Vonage API** — Telephone call integration.
- **OpenAI Whisper** — Speech recognition.
- **OpenAI GPT-4o-mini** — Natural language understanding and order extraction.
- **JavaScript** — Frontend development, where applicable.
- **Retrieval-Augmented Generation (RAG)** — Database-driven retrieval of relevant menu information.

## 🏗️ System Workflow

1. A customer calls the ordering system.
2. The telephone integration receives the call.
3. Speech is transcribed into text.
4. The language model identifies the requested products and quantities.
5. The application retrieves relevant menu information and validates the order.
6. Validated order data is stored in the database.
7. Staff can review and manage orders through the dashboard.

## 📊 Evaluation

The prototype was evaluated through functional test cases and a user study.

- **Functional testing:** Test cases TC01–TC05 passed.
- **System Usability Scale (SUS):** Mean score of 84.17/100 across 12 participants.
- The evaluation provides an initial indication of usability; further testing with a larger sample is needed.


## Thesis Document

The full diploma thesis is available below:

[Read the full diploma thesis (PDF)](Voice_Order_System.pdf)

## 🎥 Demo Video

Watch the application in action!

[![Watch Demo](https://img.youtube.com/vi/Mlt6opQw3m0/hqdefault.jpg)](https://www.youtube.com/watch?v=Mlt6opQw3m0)


## ⚙️ Installation and Configuration

1. Clone the repository:

   ```bash
   
git clone https://github.com/lefvlac/voice-order-system.git
cd voice-order-system

   ```

2. Create and activate a Python virtual environment.

3. Install the dependencies listed in `requirements.txt`, if provided.

4. Configure the required environment variables for the telephone and AI services. Use an `.env.example` file as a template if available.

5. Start the FastAPI application using the entry point and commands documented in the source code.

**Note:** API credentials are required for external services. Never commit real API keys, passwords, or private customer data.

## 🔮 Future Improvements

- Improved voice prompts and error handling.
- Menu availability and stock validation.
- Expanded functional and usability testing.
- Quantitative evaluation of speech recognition accuracy.
- Production deployment and migration to a more scalable database where appropriate.

## 👨‍💻 Author

**Eleftherios Vlachos**  
Electrical and Computer Engineering Graduate, University of Patras

- GitHub: [@lefvlac](https://github.com/lefvlac)
- LinkedIn: [Eleftherios Vlachos](https://www.linkedin.com/in/eleftherios-vlachos-46083b234/)

---

Developed as an academic software engineering project exploring the practical application of Artificial Intelligence in automated telephone ordering.
