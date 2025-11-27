import uuid
import random
from nlp_model import model as nlp
from db import init_db, save_chat, create_ticket

init_db()

sessions = {}

def new_session():
    sid = str(uuid.uuid4())
    sessions[sid] = {
        "memory": {},
        "context": []
    }
    return sid

def get_session(sid):
    if sid not in sessions:
        return None
    return sessions[sid]

def route_message(session_id, user_text):
    """Main entry point: returns bot_text and metadata"""
    sid = session_id or new_session()
    session = get_session(sid)
    if not session:
        sid = new_session()
        session = get_session(sid)

    # Save user chat
    save_chat(sid, "user", user_text)

    intent, conf = nlp.predict_intent(user_text)

    order_no = nlp.extract_order_number(user_text)
    if order_no:
        session["memory"]["order_no"] = order_no

    reply = ""
    new_ticket = None

    if intent == "greeting" or any(w in user_text.lower() for w in ["hello","hi","hey"]):
        reply = ("Hi there! How can I help you today? 😊\n"
                 "You can choose from:\n🛒 Order Issue\n📦 Package Issue\n💳 Payment Issue.")
    elif intent == "order_issue" or "order" in user_text.lower() and "issue" in user_text.lower():
        reply = "I'm sorry to hear that 😕\nCan you please tell me your order number? (For example: ORDER 12345)"
    elif intent == "order_number":

        if not session["memory"].get("order_no") and nlp.extract_order_number(user_text):
            session["memory"]["order_no"] = nlp.extract_order_number(user_text)
        status = random.choice(["Pending", "Shipped", "Delivered", "Processing"])
        session["memory"]["status"] = status
        reply = (f"Okay, please wait while I check your order {session['memory'].get('order_no')}... 🔍\n"
                 f"✅ Your order {session['memory'].get('order_no')} is currently {status}.\nExpected delivery: 2–3 days. 🚚")
    elif intent == "package_issue" or "package" in user_text.lower():
        reply = "Is your package delayed, missing, or damaged? Please type one of those options."
    elif intent == "delayed" or "delayed" in user_text.lower():
        reply = ("I'm sorry to hear that. 😞\nSometimes delays happen due to high shipping volume or weather.\n"
                 "Please wait 1–2 more business days, or contact support if it still doesn't arrive.")
    elif intent == "missing" or "missing" in user_text.lower():
        reply = "Oh no! 😟 Please provide your tracking number, and I'll help check where your package is."
    elif intent == "damaged" or "damaged" in user_text.lower():
        reply = ("I’m so sorry your package arrived damaged. 😢\nPlease send a photo of the damage to support@gmail.com,\n"
                 "and we’ll arrange a replacement right away.")
    elif intent == "payment_issue" or "payment" in user_text.lower():
        reply = "Are you having trouble with a failed transaction or a refund?"
    elif intent == "failed" or "failed transaction" in user_text.lower() or "failed" in user_text.lower():
        reply = ("Please check if your card has sufficient balance or try another payment method.\n"
                 "If you were charged but didn’t receive confirmation, contact billing support.")
    elif intent == "refund" or "refund" in user_text.lower():
        reply = ("Refunds typically take 3–5 business days to process.\n"
                 "Could you share your order number for me to check the refund status?")
    elif intent == "bye" or any(w in user_text.lower() for w in ["bye","goodbye","see you"]):
        reply = "Goodbye! 👋 Have a great day!"
    elif intent == "thanks":
        reply = "You're very welcome! 😊 Glad I could help."
    else:

        reply = nlp.generate_free_response(user_text)

    # Auto-ticket
    if "missing" in user_text.lower() and session["memory"].get("order_no"):
        ticket_id = create_ticket(session["memory"].get("order_no"), "missing", user_text)
        new_ticket = ticket_id
        reply += f"\n\n✅ I created a support ticket for you: #{ticket_id}. Our team will follow up."

    # Save bot chat
    save_chat(sid, "bot", reply)

    return {
        "session_id": sid,
        "reply": reply,
        "intent": intent,
        "confidence": conf,
        "memory": session["memory"],
        "ticket_id": new_ticket
    }

if __name__ == "__main__":
    sid = new_session()
    print("Session:", sid)
    while True:
        u = input("You: ")
        if u.lower() in ("quit", "exit"):
            break
        out = route_message(sid, u)
        print("Bot:", out["reply"])
