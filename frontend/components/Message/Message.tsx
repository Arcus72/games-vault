"use client";

import { useEffect, useState } from "react";
import "./Message.css";

type MessageType = "success" | "error";
type Msg = { id: number; text: string; type: MessageType };

export function showMessage(text: string, type: MessageType = "success") {
  window.dispatchEvent(new CustomEvent("app-message", { detail: { text, type } }));
}

export default function Messages() {
  const [messages, setMessages] = useState<Msg[]>([]);

  useEffect(() => {
    const onMessage = (e: Event) => {
      const msg = { id: Date.now() + Math.random(), ...(e as CustomEvent).detail };
      setMessages((m) => [...m, msg]);
      setTimeout(() => setMessages((m) => m.filter((x) => x.id !== msg.id)), 4000);
    };
    window.addEventListener("app-message", onMessage);
    return () => window.removeEventListener("app-message", onMessage);
  }, []);

  return (
    <div className="messages" role="status" aria-live="polite">
      {messages.map((m) => (
        <div key={m.id} className={`message message--${m.type}`}>
          {m.text}
        </div>
      ))}
    </div>
  );
}
