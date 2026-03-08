import { useState, useRef, useEffect } from "react";
import { Send, Copy, RotateCcw, User, Bot, Loader2 } from "lucide-react";
import { api } from "../api";
import { toast } from "sonner";

interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatPanelProps {
    onCodeDetected: (code: string) => void;
}

/** Lightweight markdown-ish renderer (no external deps) */
function renderMarkdown(text: string) {
    // Escape HTML
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Code blocks  ```lang\n...\n```
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_m, _lang, code) => {
        return `<pre class="bg-background border border-border rounded-lg p-3 my-2 overflow-x-auto"><code>${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code class="bg-background px-1.5 py-0.5 rounded text-accent text-xs">$1</code>');

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italic
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3 class="text-base font-bold mt-3 mb-1">$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold mt-3 mb-1">$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold mt-3 mb-1">$1</h1>');

    // Unordered lists
    html = html.replace(/^[*-] (.+)$/gm, '<li class="ml-4 list-disc">$1</li>');

    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal">$1</li>');

    // Line breaks (double newline = paragraph, single = <br>)
    html = html.replace(/\n\n/g, "</p><p class='mt-2'>");
    html = html.replace(/\n/g, "<br/>");

    return `<p>${html}</p>`;
}

export function ChatPanel({ onCodeDetected }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "Hello! I'm your SmartAPI Agent. Ingest a documentation PDF to get started, then ask me anything about it." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userQuery = input.trim();
        setInput("");
        setMessages(prev => [...prev, { role: "user", content: userQuery }]);
        setLoading(true);

        try {
            const response = await api.chat(userQuery);
            setMessages(prev => [...prev, { role: "assistant", content: response.answer }]);
            if (response.code) {
                onCodeDetected(response.code);
            }
        } catch (err: any) {
            setMessages(prev => [...prev, { role: "assistant", content: `Error: ${err.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    const copyMessage = (content: string) => {
        navigator.clipboard.writeText(content);
        toast.success("Copied to clipboard");
    };

    return (
        <div className="flex-1 flex flex-col min-w-0 bg-background relative">
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
            >
                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`flex gap-3 group ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center ${msg.role === 'user' ? 'bg-accent' : 'bg-card border border-border'
                            }`}>
                            {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-accent" />}
                        </div>

                        <div className={`flex flex-col gap-1.5 max-w-[80%] ${msg.role === 'user' ? 'items-end' : ''}`}>
                            <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                    ? 'bg-accent text-white rounded-tr-sm'
                                    : 'bg-card border border-border rounded-tl-sm'
                                }`}>
                                <div
                                    className="prose-content"
                                    dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
                                />
                            </div>

                            {msg.role === 'assistant' && (
                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-1">
                                    <button
                                        onClick={() => copyMessage(msg.content)}
                                        className="p-1 text-muted hover:text-accent transition-colors"
                                        title="Copy"
                                    >
                                        <Copy className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-lg bg-card border border-border flex items-center justify-center">
                            <Bot className="w-4 h-4 text-accent" />
                        </div>
                        <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                            <div className="flex gap-1.5">
                                <span className="w-2 h-2 bg-muted rounded-full animate-bounce"></span>
                                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></span>
                                <span className="w-2 h-2 bg-muted rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-border bg-card/50">
                <div className="max-w-3xl mx-auto relative">
                    <textarea
                        rows={1}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        placeholder="Ask a question about your ingested docs..."
                        className="w-full bg-background border border-border rounded-xl py-3 pl-4 pr-12 focus:outline-none focus:border-accent transition-colors resize-none text-sm"
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-all disabled:opacity-40"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </button>
                </div>
                <p className="text-[10px] text-center text-muted mt-1.5 opacity-60">
                    Enter to send · Shift+Enter for new line
                </p>
            </div>
        </div>
    );
}
