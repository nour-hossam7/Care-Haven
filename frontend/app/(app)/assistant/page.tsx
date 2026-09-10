"use client";

import { FormEvent, useRef, useState } from "react";
import { Button } from "@/components/Button";
import { ChatMessage } from "@/components/ChatMessage";
import { ErrorState } from "@/components/ErrorState";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const text = question.trim();
    if (!text) return;
    setQuestion("");
    setError(null);
    setMessages((current) => [...current, { role: "user", content: text }]);
    setLoading(true);
    try {
      const response = await api.chat(text);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
        },
      ]);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE;
      setError(message);
    } finally {
      setLoading(false);
      requestAnimationFrame(() => {
        listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
      });
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-3xl flex-col">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">AI assistant</h1>
        <p className="mt-1 text-sm text-slate-600">
          Questions are sent to the FastAPI <code>/chat</code> endpoint. The frontend never
          calls the language model directly.
        </p>
      </div>
      <div
        ref={listRef}
        className="mt-6 flex-1 space-y-4 overflow-y-auto rounded-2xl border border-slate-200 bg-slate-50 p-4"
      >
        {messages.length === 0 ? (
          <p className="text-sm text-slate-600">
            Ask about humanitarian needs assessment, case support, or CareHaven workflows.
          </p>
        ) : null}
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className="space-y-3">
            <ChatMessage role={message.role} content={message.content} />
          </div>
        ))}
        {loading ? (
          <p className="text-sm text-slate-500" role="status">
            The assistant is preparing an answer…
          </p>
        ) : null}
      </div>
      {error ? <div className="mt-4"><ErrorState message={error} /></div> : null}
      <form className="mt-4 flex gap-3" onSubmit={onSubmit}>
        <label className="sr-only" htmlFor="question">
          Question
        </label>
        <input
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a question"
          className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none ring-brand-600 focus:ring-2"
        />
        <Button type="submit" disabled={loading || !question.trim()}>
          Send
        </Button>
      </form>
    </div>
  );
}
