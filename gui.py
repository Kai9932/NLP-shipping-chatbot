import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout

API_URL = "http://127.0.0.1:8000/chat"

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session_id = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("NLP Chatbot")
        self.setGeometry(200,200,600,500)
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        h = QHBoxLayout()
        h.addWidget(self.input_line)
        h.addWidget(send_btn)

        layout.addWidget(QLabel("NLP Chatbot (All features)"))
        layout.addWidget(self.chat_display)
        layout.addLayout(h)

        self.setLayout(layout)
        self.show()

    def append(self, who, text):
        self.chat_display.append(f"<b>{who}:</b> {text}")

    def send_message(self):
        text = self.input_line.text().strip()
        if not text:
            return
        self.append("You", text)
        payload = {"session_id": self.session_id, "message": text}
        try:
            res = requests.post(API_URL, json=payload).json()
            bot_text = res.get("reply", "...")
            self.session_id = res.get("session_id", self.session_id)
            self.append("Bot", bot_text)
        except Exception as e:
            self.append("Bot", f"Error contacting API: {e}")
        finally:
            self.input_line.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ChatWindow()
    sys.exit(app.exec_())
